import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
import sys 
import numpy as np
import os

pd.set_option('display.max_columns', 500)
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
metric = config["metric"]

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
extra_runs = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Extra Runs': []})

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            median_cost = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Cost':[], 'Workload': [], 'Runtime':[], 'Best Runtime': [], 'Best Cost': []})
            # plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = parseLogsAll(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
            if len(runtimes) == 0:
                continue
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num', 'Completed'])
            if "Runtime" in metric:
                df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            else:
                df["Cost"] = df["Runtime"]
            # df_select = df[df['Budget'].isin(steps)]
            df_select = pd.DataFrame(df)
            df_select['Algorithms'] = df['Algorithms'].str.upper()
            # print(df_select)


            # runtimes = getAll(app, system, datasize, dataset=config["dataset"])
            # df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            # df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            # min_runtime = df['Runtime'].min()

            cost = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Cost':[], 'Experiment': [], 'Runtime': [], 'Best Runtime': [], 'Best Cost': []})

            for eid in range(config["num_of_runs"]):
                df_eid = df_select[df_select['Experiment']== eid]
                # print(df_eid)
                for budget in steps:

                    df_grouped = df_eid[df_eid['Budget'] <= budget].groupby(['Algorithms']) #.describe(percentiles=[0.05, 0.5, 0.95])
                    df_sum = df_grouped['Cost', 'Runtime'].sum()
                    df_sum = df_sum.reset_index()
                    df_sum = df_sum.set_index(['Algorithms'])
                    # print(df_sum)
                    df_grouped = df_eid[df_eid['Budget'] <= budget]
                    df_sum["Best Runtime"] = df_grouped[df_grouped['Completed']==True].groupby(['Algorithms'])['Runtime'].min()
                    df_sum["Best Cost"] = df_grouped[df_grouped['Completed']==True].groupby(['Algorithms'])['Cost'].min()
                    # print(df_sum)
                    df_sum = df_sum.reset_index()
                    df_sum["Experiment"] = eid
                    df_sum["Budget"] = budget
                    cost = cost.append(df_sum)
                
            temp = cost.groupby(['Algorithms', 'Budget'])['Cost', 'Best Runtime', 'Runtime', 'Best Cost'].median().reset_index()
            temp["Workload"] = title 
            median_cost = median_cost.append(temp)
            # print(median_cost)



            medians = median_cost.groupby(['Budget', 'Algorithms'])['Cost', 'Best Runtime', 'Runtime', 'Best Cost'].median()

            medians = medians.reset_index()

            
            # print(medians)
            for algo in medians['Algorithms'].unique():
                # print(algo)
                # print(medians[(medians['Algorithms']==algo) & (medians["Budget"]==6.0)].iloc[0].values[2:])
                base_opt_cost, base_best_runtime, base_opt_time, base_best_ecost = medians[(medians['Algorithms']==algo) & (medians["Budget"]==6.0)].iloc[0].values[2:]
                for budget in steps[1:]:
                    curr_opt_cost, curr_best_runtime, curr_opt_time, curr_best_ecost = medians[(medians['Algorithms']==algo) & (medians["Budget"]==budget)].iloc[0].values[2:]
                    if config["metric"]== "Runtime":
                        extra = (curr_opt_time - base_opt_time)/(base_best_runtime-curr_best_runtime)
                    else:
                        extra = (curr_opt_cost - base_opt_cost)/(base_best_ecost-curr_best_ecost)
                    print(algo, budget, extra, base_best_ecost, curr_best_ecost)
                    extra_runs = extra_runs.append({'Algorithms': algo, 'Budget': int(budget), 'Extra Runs': extra}, ignore_index=True)

plt.figure(figsize=(4, 2))
extra_runs["Budget"] = extra_runs["Budget"].astype(int)
print(extra_runs.groupby('Algorithms')['Extra Runs'].describe())
# print(extra_runs)
# ax = sns.lineplot(x='Budget', y='Extra Runs', hue='Algorithms', data=extra_runs, style="Algorithms",markers=True)
ax = sns.barplot(x='Budget', y='Extra Runs', hue='Algorithms', data=extra_runs, ci=None)
h, l = ax.get_legend_handles_labels()
# print(l)
if config["legends_outside"]:
    ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=transform_labels(l))
else:
    ax.legend(loc='upper left',  ncol=config["legend_cols"], prop={'size': 9} , handles=h, labels=transform_labels(l))

# if "Runtime" not in config["metric"]:
#     ax.set_yscale('log')

# ax.get_legend().set_title()
# ax.set_ylim(bottom=0)
# plt.xticks(steps[1:])
dir = 'plots/breakeven/' + prefix 
os.makedirs(dir, exist_ok=True)
plt.savefig(dir+ '/breakeven.pdf', bbox_inches = "tight")
# plt.show()
    