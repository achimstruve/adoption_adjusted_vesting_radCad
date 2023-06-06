import numpy as np
from .utils import *


# Policy Functions
def vest_tokens(params, substep, state_history, prev_state):
    """
    Determine the vesting rate into the ecosystem at this timestep
    """
    # get vesting rate from previous timestep
    previous_vesting_rate = prev_state['vesting_rate']

    # get token_price from previous timestep
    previous_token_price = state_history[-1][-1]['token_price']

    # get token_price from penultimate timestep
    if len(state_history) > 1:
        penultimate_token_price = state_history[-2][-1]['token_price']
    elif len(state_history) == 1:
        penultimate_token_price = state_history[-1][-1]['token_price']
    else:
        penultimate_token_price = prev_state['token_price']
    
    # calculate new vesting rate
    vesting_rate_new_raw = previous_vesting_rate * ((penultimate_token_price + (previous_token_price - penultimate_token_price) * params['AAV_derivative_factor']) / params['implied_price'])

    vesting_rate_new = float(calculate_value_with_caps(vesting_rate_new_raw,
                                          params['max_vesting_rate'],
                                          params['min_vesting_rate']))

    return {'vesting_rate_new': vesting_rate_new}


# State Update Function
def update_vesting_rate(params, substep, state_history, prev_state, policy_input):
    """
    Update the vesting rate
    """
    key = 'vesting_rate'
    value = policy_input['vesting_rate_new']
    return (key, value)

def update_circ_supply(params, substep, state_history, prev_state, policy_input):
    """
    Update the circ. supply
    """
    key = 'circ_supply'
    circ_supply = prev_state[key]
    total_supply = params['total_supply']
    value = circ_supply + total_supply * policy_input['vesting_rate_new']
    return (key, value)

def update_agent_tokens_from_vesting(params, substep, state_history, prev_state, policy_input):
    """
    Update the agent token balances from vesting
    """
    key = 'agents'
    updated_agents = prev_state[key].copy()

    total_supply = params['total_supply']
    vested_tokens = total_supply * policy_input['vesting_rate_new']

    team_vesting_weight = params['team_vesting_weight']
    foundation_vesting_weight = params['foundation_vesting_weight']
    investor_vesting_weight = params['investor_vesting_weight']

    # count stakeholder per type occurrences
    type_counts = {}
    for agent in updated_agents.keys():
        agent_type = updated_agents[agent]['type']
        if not agent_type in type_counts.keys():
            type_counts[agent_type] = 1
        else:
            type_counts[agent_type] += 1
    
    # calculate new amount of tokens for each agent according to vesting weights
    for agent in updated_agents.keys():
        agent_type = updated_agents[agent]['type']

        # get corresponding vesting weight
        if agent_type == 'team':
            vesting_weight = team_vesting_weight
        elif agent_type == 'foundation':
            vesting_weight = foundation_vesting_weight
        elif agent_type == 'early_investor':
            vesting_weight = investor_vesting_weight
        else:
            vesting_weight = 0
        
        if type_counts[agent_type] > 0:
            agent_vested_tokens = vested_tokens * (vesting_weight / 100) / type_counts[agent_type]
            updated_agents[agent]['tokens'] += agent_vested_tokens
            updated_agents[agent]['tokens_vested'] += agent_vested_tokens

    value = updated_agents
    return (key, value)