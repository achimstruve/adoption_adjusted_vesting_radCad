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
    MONTE_CARLO_RUNS = 1
    TIMESTEPS = 100

    model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

    result = simulation.run()
    df = pd.DataFrame(result)
    rdf = run.postprocessing(df)
    #print(rdf.head(10))

    monte_carlo_plot(rdf,'timestep','timestep','predator_count',3)
    plt.show()