from .parts.environment import *
from .parts.agents import *
import random


def initialize_seed(params, substep, state_history, prev_state):
    if prev_state['timestep'] == 0:
        random.seed(a=f'{prev_state["simulation"]}/{prev_state["subset"]}/{prev_state["run"]}')
    return {}

state_update_blocks = [
    {
        'policies': {
            'initialize_seed': initialize_seed,
        },
        'variables': {},
    },
    {
        # environment.py
        'policies': {
            'vest_tokens': vest_tokens
        },
        'variables': {
            'vesting_rate': update_vesting_rate,
            'circ_supply': update_circ_supply,
            'agents': update_agent_tokens_from_vesting
        }
    },
    {
        # environment.py
        'policies': {
            'change_implied_fdv_mc': change_implied_fdv_mc
        },
        'variables': {
            'implied_fdv_mc': update_implied_fdv_mc
        }
    },
    {
        # agents.py
        'policies': {
            'agents_choose_action': agents_choose_action
        },
        'variables': {
            'agents': update_agent_actions

        }
    },
    {
        # agents.py
        'policies': {
            'agents_perform_action': agents_perform_action
        },
        'variables': {
            'agents': update_agent_metrics,
            'dex_lp_tokens': update_dex_lp_tokens,
            'dex_lp_usdc': update_dex_lp_usdc,
            'token_price': update_token_price,
            'fdv_mc': update_fdv_mc,
            'mc': update_mc,
            'tokens_locked': update_tokens_locked
        }
    }
]