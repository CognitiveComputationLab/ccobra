""" Syllogistic example of the ORCA framework.

"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import orca

from models.random import Random
from models.atmosphere import Atmosphere

# Load the dataset
raw_df = pd.read_csv('Ragni2016.csv')
syl_df = orca.data.RawSylData(raw_df)
print(syl_df.get().head())

# Setup the simulation
sim = orca.Simulation(syl_df, None)

# Add the models to be analyzed
sim.add_model(Random())
sim.add_model(Atmosphere())

# Run the analysis
res_df = sim.run()
print(res_df.head())

# Plot the results
sns.set(style='white')
palette = sns.cubehelix_palette(
    len(sim.models), start=2.71, rot=0, dark=0.3, light=0.8)

sns.barplot(
    x='hit',
    y='model',
    data=res_df,
    palette=palette)

plt.ylabel('')
plt.xlabel('Accuracy')

plt.tight_layout()
plt.show()
