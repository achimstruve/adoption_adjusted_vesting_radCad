"""
Model parameters.
"""
sys_params = {
    'implied_price': [0.2],
    'implied_FDV_MC_Multiple_After_3y': [2],
    'speculation_factor': [0.5], # >= 0   ->  the higher the number the greater the random influence on market speculation (randomnes): 0 = no speculation and pure value investing; 1 = full speculation and zero value investing
    'AAV_exponent': [4],
    'max_vesting_rate': [0.005], # 0.1% per day
    'min_vesting_rate': [0.0001], # 0.1% per day
    'total_supply': [100000000],
    'avg_trading_fund_usage': [0.1], # percentage of usd_funds or tokens to be used for trading (can be max 2x higher based on randomness)
    'avg_token_lock_percentage': [30],
    'avg_token_remove_percentage': [50],
    'avg_token_incentivisation_percentage': [2],
    'team_vesting_weight': [10],
    'foundation_vesting_weight': [60],
    'investor_vesting_weight': [30]
}

initial_values = {
    'initial_vesting_rate': 0.001,
    'initial_team_usd_funds': 2000000,
    'initial_team_tokens':0,
    'initial_foundation_usd_funds': 500000,
    'initial_foundation_tokens': 1000000,
    'initial_early_investor_usd_funds':250000,
    'initial_early_investor_tokens': 0,
    'initial_market_investor_usd_funds':1000000,
    'initial_market_investor_tokens':0,
    'initial_market_cap': 20000000,
    'initial_dex_lp_tokens': 5000000
}

initial_values['initial_token_price'] = initial_values['initial_market_cap']/sys_params["total_supply"][0]
initial_values['initial_dex_lp_usdc'] = initial_values['initial_token_price'] * initial_values['initial_dex_lp_tokens']
initial_values['initial_circ_supply'] = initial_values['initial_team_tokens'] + initial_values['initial_foundation_tokens'] + initial_values['initial_early_investor_tokens'] + initial_values['initial_market_investor_tokens']
initial_values['initial_mc'] = initial_values['initial_circ_supply'] * initial_values['initial_token_price']

