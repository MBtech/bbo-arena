import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
import sys 
import numpy as np
import os

steps = [6, 12, 18, 24, 30]
# steps = [9, 15, 21, 30]
percentiles = [0.5, 0.95]
sns.set(style="whitegrid")

if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

pd.set_option('display.max_rows', None)
config = json.load(open(configJsonName, 'r'))
prefix = config["prefix"]
scores = dict()
log_dir = config["log_dir"]
value_key = config["value_key"]

# Make sure that the index name is correct for bo case 
algos = list()
for algo in config['bbo_algos']:
    if 'bo' in algo:
        for estimator in config["bo_estimators"]:
            for acq_method in config["bo_acq"][estimator]:
            
                algos.append((algo + '_' + estimator + '_' + acq_method).upper())
    else:
        algos.append(algo.upper())


scores = pd.DataFrame({ 'Algorithms': np.tile(np.repeat(algos, len(percentiles)), len(steps)), 'Score': [0.0]*len(algos)*len(steps)*len(percentiles), 
                    'Budget': np.repeat(steps, len(algos)*len(percentiles) ), 'Percentile': np.tile(percentiles, len(algos)*len(steps) )
                    }).set_index(['Algorithms', 'Budget', 'Percentile'])

slowdown_scores = pd.DataFrame({ 'Algorithms':[], 'Norm. Best Runtime': [], 'Budget': [], 'Percentile': []})

median_cost = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Cost':[], 'Workload': []})
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:

            # plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize
            print(title)
            runtimes = parseLogsAll(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num'])
            df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            # df_select = df[df['Budget'].isin(steps)]
            df_select = pd.DataFrame(df)
            df_select['Algorithms'] = df['Algorithms'].str.upper()
            # print(df_select)


            runtimes = getAll(app, system, datasize, dataset=config["dataset"])
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            min_runtime = df['Runtime'].min()

            cost = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Cost':[], 'Experiment': []})

            for eid in range(config["num_of_runs"]):
                df_eid = df_select[df_select['Experiment']== eid]
                for budget in steps:

                    df_grouped = df_eid[df_eid['Budget'] <= budget].groupby(['Algorithms']) #.describe(percentiles=[0.05, 0.5, 0.95])
                    df_sum = df_grouped['Cost'].sum()
                    df_sum = df_sum.reset_index()
                    df_sum["Experiment"] = eid
                    df_sum["Budget"] = budget
                    cost = cost.append(df_sum)
                    # print(df_sum.head())
                # sys.exit()

            temp = cost.groupby(['Algorithms', 'Budget'])['Cost'].median().reset_index()
            temp["Workload"] = title 
            median_cost = median_cost.append(temp)
                
            plt.figure(figsize=(4,2.5))
            ax = sns.boxplot(x='Budget', y='Cost', hue='Algorithms', data=cost, showfliers=False)
            h, l = ax.get_legend_handles_labels()
            ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=3, prop={'size': 9}, handles=h, labels=config["legends"])
            # plt.legend(loc='upper right', ncol=2, prop={'size': 8})

            dir = 'plots/opt_cost/'
            os.makedirs(dir, exist_ok=True)
            plt.savefig(dir + prefix + '_' + title +'.pdf', bbox_inches = "tight")

            # plt.show()

plt.figure(figsize=(5,3))
dir = 'plots/opt_cost/'
ax = sns.boxplot(x='Budget', y='Cost', hue='Algorithms', data=median_cost, showfliers=False)
h, l = ax.get_legend_handles_labels()
ax.legend(loc="upper left", ncol=3, prop={'size': 9}, handles=h, labels=config["legends"])

medians = median_cost.groupby(['Budget', 'Algorithms'])['Cost'].median()
print(medians)
plt.savefig(dir + prefix + '.pdf', bbox_inches = "tight")