"""
Model parameters.
"""
sys_params = {
    'supply_vesting_rate': [0.001], # 0.1% per day
    'max_vesting_rate': [0.005], # 0.1% per day
    'min_vesting_rate': [0.0001], # 0.1% per day
    'total_supply': [100000000]
}

initial_values = {
    'initial_team_usd_funds': 2000000,
    'initial_team_tokens':0,
    'initial_foundation_usd_funds': 500000,
    'initial_foundation_tokens': 1000000,
    'initial_early_investor_usd_funds':1000000,
    'initial_early_investor_tokens': 0,
    'initial_market_investor_usd_funds':1000000,
    'initial_market_investor_tokens':0,
    'initial_market_cap': 20000000,
    'initial_dex_lp_tokens': 5000000
}

initial_values['initial_token_price'] = initial_values['initial_market_cap']/sys_params["total_supply"][0]
initial_values['initial_dex_lp_usdc'] = initial_values['initial_token_price'] * initial_values['initial_dex_lp_tokens']
initial_values['initial_circ_supply'] = initial_values['initial_team_tokens'] + initial_values['initial_foundation_tokens'] + initial_values['initial_early_investor_tokens'] + initial_values['initial_market_investor_tokens']

