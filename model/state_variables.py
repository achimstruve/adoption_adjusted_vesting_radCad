from .parts.utils import *
from .sys_params import initial_values


initial_state = {
    'agents': generate_agents(initial_values['initial_team_usd_funds'],initial_values['initial_team_tokens'], 
                              initial_values['initial_foundation_usd_funds'],initial_values['initial_foundation_tokens'], 
                              initial_values['initial_early_investor_usd_funds'], initial_values['initial_early_investor_tokens'],
                              initial_values['initial_market_investor_usd_funds'], initial_values['initial_market_investor_tokens']),
    'token_price': initial_values['initial_token_price'],
    'dex_lp_tokens': initial_values['initial_dex_lp_tokens'],
    'dex_lp_usdc': initial_values['initial_dex_lp_usdc'],
    'fdv_mc': initial_values['initial_market_cap'],
    'circ_supply': initial_values['initial_circ_supply'],
    'mc': initial_values['initial_circ_supply'] * initial_values['initial_token_price'],
    'tokens_locked': 0
}