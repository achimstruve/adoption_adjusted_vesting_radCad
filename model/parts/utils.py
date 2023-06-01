import numpy as np
import random
from typing import *
import uuid
import matplotlib.pyplot as plt
import pandas as pd

# Initialization
def new_agent(stakeholder: str, usd_funds: int,
              tokens: int, action_list: list, action_weights: Tuple) -> dict:
    agent = {'type': stakeholder,
             'usd_funds': usd_funds,
             'tokens': tokens,
             'action_list': action_list,
             'action_weights': action_weights}
    return agent


def generate_agents(initial_team_usd_funds: int, initial_team_tokens: int,
                    initial_foundation_usd_funds: int, initial_foundation_tokens: int,
                    initial_early_investor_usd_funds: int, initial_early_investor_tokens: int,
                    initial_market_investor_usd_funds: int, initial_market_investor_tokens: int) -> Dict[str, dict]:
    initial_agents = {}
    team_agent = new_agent('team', initial_team_usd_funds, initial_team_tokens, ['buy', 'sell', 'lock', 'hold'], (0,0,0,100))
    foundation_agent = new_agent('foundation', initial_foundation_usd_funds, initial_foundation_tokens, ['buy', 'sell', 'lock', 'hold', 'incentivise'], (0,0,0,50,50))
    early_investor_agent = new_agent('early_investor', initial_early_investor_usd_funds, initial_early_investor_tokens, ['buy', 'sell', 'lock', 'hold'], (10,50,20,20))
    market_investor_agent = new_agent('market_investor', initial_market_investor_usd_funds, initial_market_investor_tokens, ['buy', 'sell', 'lock', 'hold'], (50,10,20,20))
    initial_agents[uuid.uuid4()] = team_agent
    initial_agents[uuid.uuid4()] = foundation_agent
    initial_agents[uuid.uuid4()] = early_investor_agent
    initial_agents[uuid.uuid4()] = market_investor_agent
    return initial_agents


# Environment
@np.vectorize
def calculate_increment(value, rate, max_rate, min_rate):
    if (rate >= min_rate) and (rate <= max_rate):
        applied_rate = rate
    elif rate < min_rate:
        applied_rate = min_rate
    else:
        applied_rate = max_rate
    new_value = value + applied_rate
    return new_value

# Location heper
def check_location(position: tuple,
                   all_sites: np.matrix,
                   busy_locations: List[tuple]) -> List[tuple]:
    """
    Returns an list of available location tuples neighboring an given
    position location.
    """
    N, M = all_sites.shape
    potential_sites = [(position[0], position[1] + 1),
                       (position[0], position[1] - 1),
                       (position[0] + 1, position[1]),
                       (position[0] - 1, position[1])]
    potential_sites = [(site[0] % N, site[1] % M) for site in potential_sites]
    valid_sites = [site for site in potential_sites if site not in busy_locations]
    return valid_sites


def get_free_location(position: tuple,
                      all_sites: np.matrix,
                      used_sites: List[tuple]) -> tuple:
    """
    Gets an random free location neighboring an position. Returns False if
    there aren't any location available.
    """
    available_locations = check_location(position, all_sites, used_sites)
    if len(available_locations) > 0:
        return random.choice(available_locations)
    else:
        return False


def nearby_agents(location: tuple, agents: Dict[str, dict]) -> Dict[str, dict]:
    """
    Filter the non-nearby agents.
    """
    neighbors = {label: agent for label, agent in agents.items()
                 if is_neighbor(agent['location'], location)}
    return neighbors


def is_neighbor(location_1: tuple, location_2: tuple) -> bool:
    dx = np.abs(location_1[0] - location_2[0])
    dy = (location_1[1] - location_2[0])
    distance = dx + dy
    if distance == 1:
        return True
    else:
        return False

# plotting
def aggregate_runs(df,aggregate_dimension):
    '''
    Function to aggregate the monte carlo runs along a single dimension.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.

    Example run:
    mean_df,median_df,std_df,min_df = aggregate_runs(df,'timestep')
    '''

    mean_df = df.groupby(aggregate_dimension).mean().reset_index()
    median_df = df.groupby(aggregate_dimension).median().reset_index()
    std_df = df.groupby(aggregate_dimension).std().reset_index()
    min_df = df.groupby(aggregate_dimension).min().reset_index()

    return mean_df,median_df,std_df,min_df

def monte_carlo_plot(df,aggregate_dimension,x,y,runs):
    '''
    A function that generates timeseries plot of Monte Carlo runs.

    Parameters:
    df: dataframe name
    aggregate_dimension: the dimension you would like to aggregate on, the standard one is timestep.
    x = x axis variable for plotting
    y = y axis variable for plotting
    run_count = the number of monte carlo simulations

    Example run:
    monte_carlo_plot(df,'timestep','timestep','revenue',run_count=100)
    '''
    mean_df,median_df,std_df,min_df = aggregate_runs(df,aggregate_dimension)
    plt.figure(figsize=(10,6))
    for r in range(1,runs+1):
        legend_name = 'Run ' + str(r)
        plt.plot(df[df.run==r].timestep, df[df.run==r][y], label = legend_name )
    plt.plot(mean_df[x], mean_df[y], label = 'Mean', color = 'black')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel(x)
    plt.ylabel(y)
    title_text = 'Performance of ' + y + ' over ' + str(runs) + ' Monte Carlo Runs'
    plt.title(title_text)