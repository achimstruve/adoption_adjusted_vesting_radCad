# Dependences
import pandas as pd
import numpy as np

# radCAD
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

# Experiments
from model import run
from model.parts.utils import *
pd.options.display.float_format = '{:.2f}'.format


from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model.sys_params import sys_params

if __name__ == '__main__':
    MONTE_CARLO_RUNS = 3
    TIMESTEPS = 365

    model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

    result = simulation.run()
    df = pd.DataFrame(result)
    rdf = run.postprocessing(df)
    
    """     monte_carlo_plot(rdf,'timestep','timestep','team_tokens',3)
    monte_carlo_plot(rdf,'timestep','timestep','foundation_tokens',3)
    monte_carlo_plot(rdf,'timestep','timestep','early_investor_tokens',3)
    monte_carlo_plot(rdf,'timestep','timestep','market_investor_tokens',3)

    monte_carlo_plot(rdf,'timestep','timestep','team_tokens_locked',3)
    monte_carlo_plot(rdf,'timestep','timestep','foundation_tokens_locked',3)
    monte_carlo_plot(rdf,'timestep','timestep','early_investor_tokens_locked',3)
    monte_carlo_plot(rdf,'timestep','timestep','market_investor_tokens_locked',3)

    monte_carlo_plot(rdf,'timestep','timestep','token_price',3)
    monte_carlo_plot(rdf,'timestep','timestep','dex_lp_tokens',3)
    monte_carlo_plot(rdf,'timestep','timestep','dex_lp_usdc',3)

    monte_carlo_plot(rdf,'timestep','timestep','team_usd_funds',3)
    monte_carlo_plot(rdf,'timestep','timestep','foundation_usd_funds',3)
    monte_carlo_plot(rdf,'timestep','timestep','early_investor_usd_funds',3)
    monte_carlo_plot(rdf,'timestep','timestep','market_investor_usd_funds',3) """

    monte_carlo_plot(rdf,'timestep','timestep','foundation_tokens_vested',4)
    monte_carlo_plot(rdf,'timestep','timestep','early_investor_tokens_vested',4)
    monte_carlo_plot(rdf,'timestep','timestep','vesting_rate',4)
    monte_carlo_plot(rdf,'timestep','timestep','token_price',4)
    plt.show()