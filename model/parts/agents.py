from .utils import *
import random
from uuid import uuid4

# Policy Functions
def agents_choose_action(params, substep, state_history, prev_state):
    agents = prev_state['agents']
    # decide for next action of each agent
    agents_action = {}
    for agent in agents.keys():
        a_type = agents[agent]["type"]
        a_usd_funds = agents[agent]["usd_funds"]
        a_tokens = agents[agent]["tokens"]
        a_tokens_locked = agents[agent]["tokens_locked"]
        a_action_list = agents[agent]["action_list"]
        a_action_weights = agents[agent]["action_weights"]
        # can't buy tokens without funds
        if a_usd_funds <= 0:
            a_action_list, a_action_weights = remove_actions('buy', a_action_list, a_action_weights)
        # can't sell, lock, or incentivise with tokens without tokens held
        if a_tokens <= 0:
            a_action_list, a_action_weights = remove_actions('sell', a_action_list, a_action_weights)
            a_action_list, a_action_weights = remove_actions('lock', a_action_list, a_action_weights)
            if 'incentivise' in a_action_list:
                a_action_list, a_action_weights = remove_actions('incentivise', a_action_list, a_action_weights)
        # can't remove locked tokens without locked tokens
        if a_tokens_locked <= 0:
            a_action_list, a_action_weights = remove_actions('remove_locked_tokens', a_action_list, a_action_weights)
        
        action = random.choices(a_action_list, weights=a_action_weights, k=1)[0]
        agents_action[agent] = action
    return {'agents_action': agents_action}

def agents_perform_action(params, substep, state_history, prev_state):
    current_timestep = state_history[-1][-1]['timestep'] + 1

    agents = prev_state['agents']
    tokens_locked = prev_state['dex_lp_usdc']
    dex_lp_tokens = prev_state['dex_lp_tokens']
    dex_lp_usdc = prev_state['dex_lp_usdc']
    constant_product = dex_lp_tokens * dex_lp_usdc
    
    agents_buy = {}
    agents_sell = {}
    agents_lock = {}
    agents_remove = {}
    agents_incentivise = {}
    bought_tokens_usd = 0
    sold_tokens_usd = 0
    locked_tokens_before_incentivisation = 0
    locked_tokens = 0
    removed_tokens = 0
    incentivised_tokens = 0

    # aggregate key metrics to each individual agent
    for agent in agents.keys():
        action = agents[agent]['current_action']
        if action == 'buy':
            agents_buy[agent] = params['avg_usd_base_buy'] * (1 + current_timestep / 100)
        if action == 'sell':
            agents_sell[agent] = params['avg_usd_sell'] * (1 - current_timestep / 2000)
            sold_tokens_usd += agents_sell[agent]
        if action == 'lock':
            agents_lock[agent] = agents[agent]['tokens'] * (params['avg_token_lock_percentage'] / 100)
            locked_tokens_before_incentivisation += agents_lock[agent]
        if action == 'remove_locked_tokens':
            agents_remove[agent] = agents[agent]['tokens_locked'] * (params['avg_token_remove_percentage'] / 100)
        if action == 'incentivise':
            agents_incentivise[agent] = agents[agent]['tokens'] * (params['avg_token_incentivisation_percentage'] / 100)
            incentivised_tokens += agents_incentivise[agent]
    
    # cancel incentivisation if no tokens locked
    if locked_tokens_before_incentivisation <= 0:
        incentivised_tokens = 0

    # increase bought and locked tokens and decrease removed tokens, if incentivised
    for agent in agents.keys():
        action = agents[agent]['current_action']

        if incentivised_tokens > 0:
            if action == 'buy':
                agents_buy[agent] = agents_buy[agent] * (1 + incentivised_tokens / params['total_supply'] * params['avg_incentivisation_buy_factor'])
                bought_tokens_usd += agents_buy[agent]
            if action == 'lock':
                agents_lock[agent] = agents_lock[agent] * (1 + incentivised_tokens / params['total_supply'] * params['avg_incentivisation_lock_factor'])
                locked_tokens += agents_lock[agent]
            if action == 'remove_locked_tokens':
                agents_remove[agent] = agents_remove[agent] * (1 - incentivised_tokens / params['total_supply'] * params['avg_incentivisation_remove_factor'])
                removed_tokens += agents_remove[agent]
        else:
            if action == 'incentivise':
                agents_incentivise[agent] = 0

    #print(agents_buy, agents_sell, agents_lock, agents_remove, agents_incentivise)
    # perform buys / sells / token locks / token removals / token incentivisations of all agents in a random order
    updated_agents = agents.copy()
    shuffled_agents = shuffle_dict(updated_agents)
    for agent in shuffled_agents:
        # agent action
        action = agents[agent]['current_action']

        # token incentivisation
        if locked_tokens > 0:
            # calculate share of locked tokens
            locked_tokens_share = updated_agents[agent]['tokens_locked'] / locked_tokens
            # receive tokens from incentivisation
            updated_agents[agent]['tokens'] += incentivised_tokens * locked_tokens_share

        # buy tokens from the DEX
        if action == 'buy':
            # check if agent has enough funds to buy tokens worth of agents_buy
            if agents_buy[agent] > agents[agent]['usd_funds']:
                agents_buy[agent] = agents[agent]['usd_funds']
            updated_agents[agent]['usd_funds'] -= agents_buy[agent]
            updated_agents[agent]['tokens'] += dex_lp_tokens * (1 - (dex_lp_usdc / (dex_lp_usdc + agents_buy[agent])))
            dex_lp_usdc += agents_buy[agent]
            dex_lp_tokens = constant_product / dex_lp_usdc
        
        if action == 'sell':
            # check if agent has enough tokens to sell the equivalent amount of agents_sell[agent]
            if agents_sell[agent] > dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + agents[agent]['tokens']))):
                agents_sell[agent] = dex_lp_usdc * (1 - (dex_lp_tokens / (dex_lp_tokens + agents[agent]['tokens'])))
            updated_agents[agent]['usd_funds'] += agents_sell[agent]
            updated_agents[agent]['tokens'] -= dex_lp_tokens * ((dex_lp_usdc / (dex_lp_usdc - agents_sell[agent])) - 1)
            dex_lp_usdc -= agents_sell[agent]
            dex_lp_tokens = constant_product / dex_lp_usdc
        
        if action == 'lock':
            # check if agent has enough tokens to lock
            if updated_agents[agent]['tokens'] < agents_lock[agent]:
                agents_lock[agent] = updated_agents[agent]['tokens']
            updated_agents[agent]['tokens'] -= agents_lock[agent]
            updated_agents[agent]['tokens_locked'] += agents_lock[agent]
            tokens_locked += agents_lock[agent]
        
        if action == 'remove_locked_tokens':
            # check if agent has enough tokens locked to remove
            if updated_agents[agent]['tokens_locked'] < agents_remove[agent]:
                agents_remove[agent] = updated_agents[agent]['tokens_locked']
            updated_agents[agent]['tokens'] += agents_remove[agent]
            updated_agents[agent]['tokens_locked'] -= agents_remove[agent]
            tokens_locked -= agents_remove[agent]
        
        if action == 'incentivise':
            if agents_incentivise[agent] > updated_agents[agent]['tokens']:
                agents_incentivise[agent] = updated_agents[agent]['tokens']
            updated_agents[agent]['tokens'] -= agents_incentivise[agent]
    
    token_price = dex_lp_usdc / dex_lp_tokens

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