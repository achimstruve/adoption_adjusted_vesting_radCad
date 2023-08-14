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
             'tokens_vested': 0,
             'tokens_locked': 0,
             'action_list': action_list,
             'action_weights': action_weights,
             'current_action': 'hold'}
    return agent


def generate_agents(initial_team_usd_funds: int, initial_team_tokens: int,
                    initial_foundation_usd_funds: int, initial_foundation_tokens: int,
                    initial_early_investor_usd_funds: int, initial_early_investor_tokens: int,
                    initial_market_investor_usd_funds: int, initial_market_investor_tokens: int) -> Dict[str, dict]:
    initial_agents = {}
    team_agent = new_agent('team', initial_team_usd_funds, initial_team_tokens, ['trade', 'hold', 'lock', 'remove_locked_tokens'], (0,0,100,0))
    foundation_agent = new_agent('foundation', initial_foundation_usd_funds, initial_foundation_tokens, ['trade', 'hold', 'lock', 'remove_locked_tokens', 'incentivise'], (0,50,0,0,50))
    early_investor_agent = new_agent('early_investor', initial_early_investor_usd_funds, initial_early_investor_tokens, ['trade', 'hold', 'lock', 'remove_locked_tokens'], (60,20,6,14))
    market_investor_agent = new_agent('market_investor', initial_market_investor_usd_funds, initial_market_investor_tokens, ['trade', 'hold', 'lock', 'remove_locked_tokens'], (60,15,16,9))
    initial_agents[uuid.uuid4()] = team_agent
    initial_agents[uuid.uuid4()] = foundation_agent
    initial_agents[uuid.uuid4()] = early_investor_agent
    initial_agents[uuid.uuid4()] = market_investor_agent
    return initial_agents

# Agent Behavior Helper
def remove_actions(action, action_list, action_weights):
    idx = action_list.index(action)
    new_action_list = action_list
    new_action_list.remove(action)
    weights_lst = list(action_weights)
    weights_lst.pop(idx)
    action_weights = tuple(weights_lst)
    return new_action_list, action_weights

def change_action_probability(action, action_list, action_weights, added_prob_value):
    idx = action_list.index(action)
    weights_lst = list(action_weights)
    if (weights_lst[idx] + added_prob_value) > 100:
        added_prob_value = 100 - weights_lst[idx]
    
    # count non-zero weights
    non_zero_weight_count = np.count_nonzero(weights_lst)
    if non_zero_weight_count > 1:
        removed_prob_value = added_prob_value / (np.count_nonzero(weights_lst) - 1)
    elif non_zero_weight_count == 1:
        removed_prob_value = added_prob_value
    else:
        removed_prob_value = 0
    
    for i in range(len(weights_lst)):
        if i != idx:
            if weights_lst[i] - removed_prob_value > 0:
                weights_lst[i] -= removed_prob_value
            else:
                weights_lst[i] = 0
        else:
            weights_lst[i] += added_prob_value
    action_weights = tuple(weights_lst)
    return action_list, action_weights

def shuffle_dict(dictionary):
    l = list(dictionary.items())
    random.shuffle(l)
    return dict(l)

# Environment
@np.vectorize
def calculate_value_with_caps(rate, max_rate, min_rate):
    if (rate >= min_rate) and (rate <= max_rate):
        applied_rate = rate
    elif rate < min_rate:
        applied_rate = min_rate
    else:
        applied_rate = max_rate
    return applied_rate

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