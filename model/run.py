import pandas as pd
from .parts.utils import * 


def postprocessing(df):
    '''
    Definition:
    Refine and extract metrics from the simulation
    
    Parameters:
    df: simulation dataframe
    '''
    # subset to last substep
    df = df[df['substep'] == df.substep.max()]

    # Get the ABM results
    agent_ds = df.agents
    token_price_ds = df.token_price
    dex_lp_tokens_ds = df.dex_lp_tokens
    dex_lp_usdc_ds = df.dex_lp_usdc
    fdv_mc_ds = df.fdv_mc
    implied_fdv_mc_ds = df.implied_fdv_mc
    mc_ds = df.mc
    circ_supply_ds = df.circ_supply
    tokens_locked_ds = df.tokens_locked
    vesting_rate_ds = df.vesting_rate
    timesteps = df.timestep
    
    # Get metrics

    ## Agent quantity
    team_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'team']))
    foundation_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'foundation']))
    early_investor_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'early_investor']))
    market_investor_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'market_investor']))


    ## agents tokens quantitiy
    team_tokens = agent_ds.map(lambda s: sum([agent['tokens'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'team']))
    foundation_tokens = agent_ds.map(lambda s: sum([agent['tokens'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'foundation']))
    early_investor_tokens = agent_ds.map(lambda s: sum([agent['tokens'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'early_investor']))
    market_investor_tokens = agent_ds.map(lambda s: sum([agent['tokens'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'market_investor']))
    
    ## agents usd_funds quantitiy
    team_usd_funds = agent_ds.map(lambda s: sum([agent['usd_funds'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'team']))
    foundation_usd_funds = agent_ds.map(lambda s: sum([agent['usd_funds'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'foundation']))
    early_investor_usd_funds = agent_ds.map(lambda s: sum([agent['usd_funds'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'early_investor']))
    market_investor_usd_funds = agent_ds.map(lambda s: sum([agent['usd_funds'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'market_investor']))

    ## agents tokens locked quantity
    team_tokens_locked = agent_ds.map(lambda s: sum([agent['tokens_locked'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'team']))
    foundation_tokens_locked = agent_ds.map(lambda s: sum([agent['tokens_locked'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'foundation']))
    early_investor_tokens_locked = agent_ds.map(lambda s: sum([agent['tokens_locked'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'early_investor']))
    market_investor_tokens_locked = agent_ds.map(lambda s: sum([agent['tokens_locked'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'market_investor']))

    ## agents tokens vested quantity
    team_tokens_vested = agent_ds.map(lambda s: sum([agent['tokens_vested'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'team']))
    foundation_tokens_vested = agent_ds.map(lambda s: sum([agent['tokens_vested'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'foundation']))
    early_investor_tokens_vested = agent_ds.map(lambda s: sum([agent['tokens_vested'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'early_investor']))
    market_investor_tokens_vested = agent_ds.map(lambda s: sum([agent['tokens_vested'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'market_investor']))

    # Create an analysis dataset
    data = (pd.DataFrame({'timestep': timesteps,
                          'run': df.run,
                          'token_price': token_price_ds,
                          'dex_lp_tokens': dex_lp_tokens_ds,
                          'dex_lp_usdc': dex_lp_usdc_ds,
                          'fdv_mc': fdv_mc_ds,
                          'implied_fdv_mc': implied_fdv_mc_ds,
                          'mc': mc_ds,
                          'circ_supply': circ_supply_ds,
                          'tokens_locked': tokens_locked_ds,
                          'vesting_rate': vesting_rate_ds,
                          'team_agents': team_count,
                          'foundation_agents': foundation_count,
                          'early_investor_agents': early_investor_count,
                          'market_investor_agents': market_investor_count,
                          'team_tokens': team_tokens,
                          'foundation_tokens': foundation_tokens,
                          'early_investor_tokens': early_investor_tokens,
                          'market_investor_tokens': market_investor_tokens,
                          'team_usd_funds': team_usd_funds,
                          'foundation_usd_funds': foundation_usd_funds,
                          'early_investor_usd_funds': early_investor_usd_funds,
                          'market_investor_usd_funds': market_investor_usd_funds,
                          'team_tokens_locked': team_tokens_locked,
                          'foundation_tokens_locked': foundation_tokens_locked,
                          'early_investor_tokens_locked': early_investor_tokens_locked,
                          'market_investor_tokens_locked': market_investor_tokens_locked,
                          'team_tokens_vested': team_tokens_vested,
                          'foundation_tokens_vested': foundation_tokens_vested,
                          'early_investor_tokens_vested': early_investor_tokens_vested,
                          'market_investor_tokens_vested': market_investor_tokens_vested})       
           )
    
    return data