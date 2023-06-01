import numpy as np
from .utils import *


# Behaviors
def vest_tokens(params, substep, state_history, prev_state):
    """
    Increases the token supply
    """
    new_circ_supply = calculate_increment(prev_state['circ_supply'],
                                          params['supply_vesting_rate'],
                                          params['max_vesting_rate'],
                                          params['min_vesting_rate'])
    return {'update_circ_supply': new_circ_supply}


# Mechanisms
def update_circ_supply(params, substep, state_history, prev_state, policy_input):
    key = 'circ_supply'
    value = policy_input['update_circ_supply']
    return (key, value)