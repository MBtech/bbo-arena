import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
import sys
import numpy as np
import math

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"


config = json.load(open(configJsonName, 'r'))
count = 0
good_confs = list()
all_runtimes = list()
num_of_nodes = [4, 6, 8, 10, 12]
metric = "cost"

dividers = {'large': 8, 'xlarge': 4, '2xlarge': 2, '4xlarge': 1}
indices = []
for t in types:
    for s in sizes:
        indices.append(t+'.'+s)

algos = list()
for algo in config['bbo_algos']:
    if 'bo' in algo:
        for estimator in config["bo_estimators"]:
            for acq_method in config["bo_acq"][estimator]:
            
                algos.append((algo + '_' + estimator + '_' + acq_method))
    else:
        algos.append(algo)


for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = getAll(app, system, datasize, metric=metric, dataset=config["dataset"])
            if len(runtimes) == 0:
                continue

            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            
            df["Num"] = df.apply(lambda x: (x["Num"] / dividers[x["Size"]]), axis=1)

            # df = df[df["Num"].isin(num_of_nodes)]
            df["Family"] = df['Type'] + '.'+df['Size']
            df.drop(['Type', 'Size'], axis=1, inplace=True)
            df_norm = df.copy()
            df_norm["Num"] = df_norm["Num"].astype(int)
            df_norm['Runtime'] =  df['Runtime']/df['Runtime'].min()
            df_norm['Runtime'] = df_norm['Runtime'].clip(0, 2)
            df_norm = df_norm.pivot("Num", "Family", "Runtime")
            # df_norm = df_norm.reindex(['c5.large', 'c5.xlarge', 'c5.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 
            #                                 'r4.large', 'r4.xlarge', 'r4.2xlarge'], axis=1)

            df_norm = df_norm.reindex(indices, axis=1)
            # print(df_norm)
            total_rows=len(df_norm.axes[0])
            total_cols=len(df_norm.axes[1])  
            
            


           
            runtimes = parseLogsAll(system, app, datasize, configJsonName, config['log_dir'], config['value_key'])
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num'])
            # print(df)

            for algo in algos:
                plt.figure(figsize=(6, 4))
                labels = np.full((total_rows, total_cols), "", dtype=object)
                # labels = np.empty([total_rows, total_cols], dtype=object)
                # labels = np.array([[""]*total_cols]*total_rows)
                # ax.invert_yaxis()
                max_budget = 6
                for i in range(1, max_budget+1):
                    point = df[(df['Algorithms']==algo) & (df['Experiment']==1) & (df['Budget']==i)]
                    # print(point)
                    # print(point['Type']+'.'+point['Size'])
                    t = point['Type'].iloc[0]
                    s = point['Size'].iloc[0]
                    index = indices.index(t+'.'+s)
                    # print(point['Num'])
                    labels[int(point['Num'].iloc[0]/dividers[s])-2][index] = str(i)
                
                # print(labels)
                ax = sns.heatmap(df_norm,  cbar_kws={'label': 'Norm. Exec. '+ metric}, linewidths=.5, linecolor="green", \
                            cmap=sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark"), annot=labels, fmt="", 
                            annot_kws={"color": 'yellow', "weight":'bold', 'size': 9})
                plt.title(algo)
                ax.tick_params(axis='x', which='major', labelsize=9)
                plt.xticks(rotation=90)
                plt.xlabel('Instance Type')
                plt.ylabel('Cluster Size')
            # plt.savefig('plots/data/pdf_'+ title + '.pdf', bbox_inches = "tight")
            # plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})


            # os.makedirs(dir, exist_ok=True)
            # plt.savefig('plots/heatmaps/'+metric+'/' +title+ '.pdf', bbox_inches = "tight")
            plt.show()
            # sys.exit()