import pandas as pd 
import sys
import seaborn as sns
import json
import matplotlib.pyplot as plt 

# sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

config = json.load(open(configJsonName, 'r'))
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize
            df = pd.read_csv('../algorithms/error/'+'error_'+ title + '.csv')
            ax= sns.boxplot(x="algorithm",y='rmse', data=df)
            # ax = sns.violinplot(y='rmse', x="algorithm", data=df, cut=0)
            print(df)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
            plt.title(title)
            plt.ylabel('RMSE')
            plt.xlabel('Algorithm')
            plt.savefig('plots/error/error_'+ title + '.pdf', bbox_inches = "tight")
