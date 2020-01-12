import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest
import sys 

steps = [6, 18, 30]
sns.set(style="whitegrid")

if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "best"
    
config = json.load(open(configJsonName, 'r'))
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize

            runtimes = parseLogs(system, app, datasize, configJsonName)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            df_select = df[df['Budget'].isin(steps)]
            # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])
            sns.boxplot(x='Budget', y='Best Runtime', hue="Algorithms", data=df_select)
            # sns.violinplot(x='Budget', y='Best Runtime', hue="Algorithms", data=df_select, cut=0)

            best = getBest(app, system, datasize)
            plt.axhline(best, color='blue')
            plt.title(title)
            plt.legend(loc='upper right', ncol=3, prop={'size': 7})
            plt.savefig('plots/'+prefix+'_'+ title + '.pdf', bbox_inches = "tight")
            # plt.show()
