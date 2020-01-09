import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest

steps = [6, 18, 30]
sns.set(style="whitegrid")
configJsonName = "test_configs/all_runs.json"
config = json.load(open(configJsonName, 'r'))
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize

            runtimes = parseLogs(system, app, datasize, configJsonName)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            df_select = df[df['Budget'].isin(steps)]
            # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])
            sns.boxplot(x='Budget', y='Best Runtime', hue="Algorithms", data=df_select)

            best = getBest(app, system, datasize)
            plt.axhline(best, color='blue')
            plt.title(title)
            plt.legend(loc='upper right', ncol=2, prop={'size': 9})
            plt.savefig('plots/'+'best_'+ title + '.pdf')
            # plt.show()
