import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import getAll
import sys
import numpy as np

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "opt"


config = json.load(open(configJsonName, 'r'))
count = 0
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize

            runtimes = getAll(app, system, datasize)
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            sns.distplot(np.array(df['Runtime']), kde=False, rug=True)

            plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})
            # plt.savefig('plots/data/'+ title + '.pdf', bbox_inches = "tight")

            plt.show()
