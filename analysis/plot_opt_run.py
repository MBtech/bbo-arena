import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest
import sys

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "opt"

config = json.load(open(configJsonName, 'r'))
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize

            runtimes = parseLogs(system, app, datasize, configJsonName)
            
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])
            sns.relplot(x='Budget', y='Best Runtime', hue="Algorithms", ci="sd", data=df, kind="line")

            best = getBest(app, system, datasize)
            plt.axhline(best, color='black')
            plt.xlim(0, 30)
            plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})
            plt.savefig('plots/'+prefix+'_'+ title + '.pdf')
            # plt.show()
