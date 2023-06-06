"""
Model parameters.
"""
sys_params = {
    'implied_price': 0.2,
    'AAV_derivative_factor': [50],
    'max_vesting_rate': [0.005], # 0.1% per day
    'min_vesting_rate': [0.0001], # 0.1% per day
    'total_supply': [100000000],
    'avg_usd_base_buy': [20000],
    'avg_usd_sell': [20000],
    'avg_token_lock_percentage': [30],
    'avg_token_remove_percentage': [50],
    'avg_token_incentivisation_percentage': [2],
    'avg_incentivisation_buy_factor': [10], # issued token incentives increase token buys to w.r.t sum(avg_usd_buy(agent)) * (1 + sum(incentives) / total supply) * avg_incentivisation_buy_factor
    'avg_incentivisation_lock_factor': [30],
    'avg_incentivisation_remove_factor': [30],
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

