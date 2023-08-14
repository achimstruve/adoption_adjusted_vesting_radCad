from .utils import *
import random
from uuid import uuid4

# Policy Functions
def agents_choose_action(params, substep, state_history, prev_state):
    agents = prev_state['agents'].copy()
    # decide for next action of each agent
    agents_action = {}
    for agent in agents.keys():
        a_type = agents[agent]["type"]
        a_usd_funds = agents[agent]["usd_funds"]
        a_tokens = agents[agent]["tokens"]
        a_tokens_locked = agents[agent]["tokens_locked"]
        a_action_list = agents[agent]["action_list"][:]
        a_action_weights = agents[agent]["action_weights"]

        # can't trade if no funds and no tokens available
        if (a_tokens <= 0) and (a_usd_funds <= 0):
            a_action_list, a_action_weights = remove_actions('trade', a_action_list, a_action_weights)

        # can't sell, lock, or incentivise with tokens without tokens held
        if a_tokens <= 0:
            a_action_list, a_action_weights = remove_actions('lock', a_action_list, a_action_weights)
            if 'incentivise' in a_action_list:
                a_action_list, a_action_weights = remove_actions('incentivise', a_action_list, a_action_weights)
        # can't remove locked tokens without locked tokens
        if a_tokens_locked <= 0:
            a_action_list, a_action_weights = remove_actions('remove_locked_tokens', a_action_list, a_action_weights)
        
        # increase locking probability dependent on avg_token_incentivisation_percentage
        if 'lock' in a_action_list:
            a_action_list, a_action_weights = change_action_probability('lock', a_action_list, a_action_weights, params['avg_token_incentivisation_percentage']**2)

        action = random.choices(a_action_list, weights=a_action_weights, k=1)[0]

        agents_action[agent] = action
    return {'agents_action': agents_action}

def agents_perform_action(params, substep, state_history, prev_state):
    current_timestep = state_history[-1][-1]['timestep'] + 1

    agents = prev_state['agents']
    fdv_mc = prev_state['fdv_mc']
    implied_fdv_mc = prev_state['implied_fdv_mc']
    tokens_locked = prev_state['dex_lp_usdc']
    dex_lp_tokens = prev_state['dex_lp_tokens']
    dex_lp_usdc = prev_state['dex_lp_usdc']
    token_price = dex_lp_usdc / dex_lp_tokens
    constant_product = dex_lp_tokens * dex_lp_usdc
    
    bought_tokens_usd = 0
    sold_tokens_usd = 0
    locked_tokens_before_incentivisation = 0
    locked_tokens = 0
    removed_tokens = 0
    incentivised_tokens = 0

    # aggregate key metrics to each individual agent
    updated_agents = agents.copy()
    shuffled_agents = shuffle_dict(updated_agents)
    for agent in shuffled_agents:
        action = agents[agent]['current_action']
        
        # TRADE
        if action == 'trade':
            # calculate arbitrage amount of usd_funds to be used to buy the price back up to match the implied_FDV_MC
            implied_fdv_mc_token_price = implied_fdv_mc / params['total_supply']
            implied_dex_lp_usdc = np.sqrt(constant_product * implied_fdv_mc_token_price)
            
            # VALUE INVESTING
            # BUY
            if (fdv_mc / implied_fdv_mc) < 1:
                base_buy_amt = (implied_dex_lp_usdc - dex_lp_usdc)
                if base_buy_amt >= 0:
                    usd_buy_amt = base_buy_amt * (1 - params['speculation_factor'])
                else:
                    usd_buy_amt = 0
                
                # check if agent has enough funds to buy tokens worth of agents_buy
                if usd_buy_amt > agents[agent]['usd_funds']:
                    usd_buy_amt = agents[agent]['usd_funds']
                updated_agents[agent]['usd_funds'] -= usd_buy_amt
                updated_agents[agent]['tokens'] += dex_lp_tokens * (1 - (dex_lp_usdc / (dex_lp_usdc + usd_buy_amt)))
                # update the LP
                dex_lp_usdc += usd_buy_amt
                dex_lp_tokens = constant_product / dex_lp_usdc
            
            # SELL
            elif (fdv_mc / implied_fdv_mc) > 1:
                base_sell_amt = (dex_lp_usdc - implied_dex_lp_usdc)
                if base_sell_amt >= 0:
                    usd_sell_amt = base_sell_amt * (1 - params['speculation_factor'])
                else:
                    usd_sell_amt = 0
                
                # check if agent has enough tokens to sell the equivalent amount of agents_sell[agent]
                if usd_sell_amt > dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + agents[agent]['tokens']))):
                    usd_sell_amt = dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + agents[agent]['tokens'])))
                updated_agents[agent]['usd_funds'] += usd_sell_amt
                updated_agents[agent]['tokens'] -= dex_lp_tokens * ((dex_lp_usdc / (dex_lp_usdc - usd_sell_amt)) - 1)
                # update the LP
                dex_lp_usdc -= usd_sell_amt
                dex_lp_tokens = constant_product / dex_lp_usdc
            else:
                pass
            
            # SPECULATION INVESTING -> selling vested tokens + random buying / selling behavior
            if params['speculation_factor'] > 0:
                # SELLING VESTING TOKENS
                # get vested tokens from previous timestep
                previous_vested_tokens = state_history[-1][-1]['agents'][agent]['tokens_vested']
                # get vested tokens from penultimate timestep
                if len(state_history) > 1:
                    penultimate_vested_tokens = state_history[-2][-1]['agents'][agent]['tokens_vested']
                elif len(state_history) == 1:
                    penultimate_vested_tokens = state_history[-1][-1]['agents'][agent]['tokens_vested']
                else:
                    penultimate_vested_tokens = prev_state['agents'][agent]['tokens_vested']
                vested_tokens = previous_vested_tokens - penultimate_vested_tokens

                sell_vesting_tokens = vested_tokens * (params['speculation_factor']/2) # amount of tokens to be sold from vesting
                if updated_agents[agent]['tokens'] < sell_vesting_tokens:
                    sell_vesting_tokens = updated_agents[agent]['tokens']
                sell_vesting_usdc = dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + sell_vesting_tokens))) # amount of usdc to be received by selling vested tokens
                updated_agents[agent]['usd_funds'] += sell_vesting_usdc
                updated_agents[agent]['tokens'] -= sell_vesting_tokens
                dex_lp_tokens += sell_vesting_tokens
                dex_lp_usdc = constant_product / dex_lp_tokens

                # RANDOM BUY & SELL
                trade_factor = ((random.random()-0.5)*2) # value between -1 and 1
                if trade_factor > 0:
                    buy_amt = updated_agents[agent]['usd_funds'] * params['avg_trading_fund_usage'] * (1 + trade_factor) * (params['speculation_factor']/2) # buy usdc amount
                    # check if agent has enough funds to buy tokens worth of agents_buy
                    if buy_amt > agents[agent]['usd_funds']:
                        buy_amt = agents[agent]['usd_funds']
                    updated_agents[agent]['usd_funds'] -= buy_amt
                    updated_agents[agent]['tokens'] += dex_lp_tokens * (1 - (dex_lp_usdc / (dex_lp_usdc + buy_amt)))
                    # update the LP
                    dex_lp_usdc += buy_amt
                    dex_lp_tokens = constant_product / dex_lp_usdc
                elif trade_factor < 0:
                    sell_amt = updated_agents[agent]['tokens'] * params['avg_trading_fund_usage'] * (1 + trade_factor) * (params['speculation_factor']/2) # sell token amount
                    if updated_agents[agent]['tokens'] < sell_amt:
                        updated_agents[agent]['tokens'] = sell_amt
                    updated_agents[agent]['tokens'] -= sell_amt
                    updated_agents[agent]['usd_funds'] += dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + sell_amt)))
                    # update the LP
                    dex_lp_tokens += sell_amt
                    dex_lp_usdc = constant_product / dex_lp_tokens
                else:
                    pass

            # update the token_price and the fdv_mc
            token_price = dex_lp_usdc / dex_lp_tokens
            fdv_mc = token_price * params['total_supply']
        
        # LOCK
        if action == 'lock':
            lock_amt = agents[agent]['tokens'] * (params['avg_token_lock_percentage'] / 100)
            # check if agent has enough tokens to lock
            if updated_agents[agent]['tokens'] < lock_amt:
                lock_amt = updated_agents[agent]['tokens']
            updated_agents[agent]['tokens'] -= lock_amt
            updated_agents[agent]['tokens_locked'] += lock_amt
            tokens_locked += lock_amt

        # REMOVE
        if action == 'remove_locked_tokens':
            removed_amt = agents[agent]['tokens_locked'] * (params['avg_token_remove_percentage'] / 100)
            # check if agent has enough tokens locked to remove
            if updated_agents[agent]['tokens_locked'] < removed_amt:
                removed_amt = updated_agents[agent]['tokens_locked']
            updated_agents[agent]['tokens'] += removed_amt
            updated_agents[agent]['tokens_locked'] -= removed_amt
            tokens_locked -= removed_amt

        # INCENTIVISE
        if action == 'incentivise':
            incentivise_amt = agents[agent]['tokens'] * (params['avg_token_incentivisation_percentage'] / 100)
            if incentivise_amt > updated_agents[agent]['tokens']:
                incentivise_amt = updated_agents[agent]['tokens']
            updated_agents[agent]['tokens'] -= incentivise_amt

            # distribute incentivisation tokens
            if locked_tokens > 0:
                for agent_i in updated_agents:
                    # calculate share of locked tokens
                    locked_tokens_share = updated_agents[agent]['tokens_locked'] / locked_tokens
                    # receive tokens from incentivisation
                    incentivisation_amt = incentivised_tokens * locked_tokens_share
                    updated_agents[agent]['tokens_locked'] += incentivisation_amt
                    tokens_locked += incentivisation_amt

    return {'updated_agents': updated_agents,
            'updated_dex_lp_tokens': dex_lp_tokens,
            'update_dex_lp_usdc': dex_lp_usdc,
            'updated_token_price': token_price,
            'updated_tokens_locked': tokens_locked}

# State Update Function
def update_agent_actions(params, substep, state_history, prev_state, policy_input):
    agent_actions = policy_input['agents_action']
    updated_agents = prev_state['agents'].copy()

    for agent in updated_agents.keys():
        updated_agents[agent]['current_action'] = agent_actions[agent]
    
    return('agents', updated_agents)

def update_agent_metrics(params, substep, state_history, prev_state, policy_input):
    updated_agents = policy_input['updated_agents'].copy()
    return ('agents', updated_agents)

def update_dex_lp_tokens(params, substep, state_history, prev_state, policy_input):
    updated_dex_lp_tokens = policy_input['updated_dex_lp_tokens']
    return ('dex_lp_tokens', updated_dex_lp_tokens)

def update_dex_lp_usdc(params, substep, state_history, prev_state, policy_input):
    update_dex_lp_usdc = policy_input['update_dex_lp_usdc']
    return ('dex_lp_usdc', update_dex_lp_usdc)

def update_token_price(params, substep, state_history, prev_state, policy_input):
    updated_token_price = policy_input['updated_token_price']
    return ('token_price', updated_token_price)

def update_fdv_mc(params, substep, state_history, prev_state, policy_input):
    updated_token_price = policy_input['updated_token_price']
    updated_fdv_mc = updated_token_price * params['total_supply']
    return ('fdv_mc', updated_fdv_mc)

def update_mc(params, substep, state_history, prev_state, policy_input):
    updated_token_price = policy_input['updated_token_price']

    """ for i in range(len(state_history)):
        print(i, state_history[i])
    print(len(state_history),"\n\n")
    print("circ_supply prev_state: ", prev_state["circ_supply"])
    print("circ_supply state_history of previous substep ",state_history[-1][-1]['substep'], ": ", state_history[-1][-1]['circ_supply'] )
    if len(state_history)> 2:
        bb """
    updated_mc = prev_state['circ_supply'] * updated_token_price
    return ('mc', updated_mc)

def update_tokens_locked(params, substep, state_history, prev_state, policy_input):
    updated_tokens_locked = policy_input['updated_tokens_locked']
    return ('tokens_locked', updated_tokens_locked)