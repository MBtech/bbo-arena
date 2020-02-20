import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import getAll
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
metric = "runtime"

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = getAll(app, system, datasize, metric=metric)
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            
            # df = df[df["Num"].isin(num_of_nodes)]
            df["Family"] = df['Type'] + '.'+df['Size']
            df.drop(['Type', 'Size'], axis=1, inplace=True)
            df_norm = df.copy()
            df_norm['Runtime'] =  df['Runtime']/df['Runtime'].min()
            df_norm['Runtime'] = df_norm['Runtime'].clip(0, 2)
            df_norm = df_norm.pivot("Num", "Family", "Runtime")
            df_norm = df_norm.reindex(['c4.large', 'c4.xlarge', 'c4.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 'r4.large', 'r4.xlarge', 'r4.2xlarge'], axis=1)
            print(df_norm)

            max_runtime = df['Runtime'].max()
            r = max_runtime / df['Runtime'].min()
            print(r)

            min_runtime = df['Runtime'].min()
            runtime_threashold = 1.1*min_runtime
            good_confs.append([title, len(df[df['Runtime']<=runtime_threashold])])

            # Measuring random pick probability
            thresholds = ['1.1', '1.2', '1.5']
            probabilities = pd.DataFrame({'Budget':[], 'Threshold': [], 'Probability': []})
            for threshold in thresholds:
                print(threshold)
                prob = len(df[df['Runtime']<=min_runtime*float(threshold)])/len(df)
                for num in range(1, config["budget"]+1):
                    probabilities = probabilities.append({'Probability': (1 - (1 - prob)**num ), 'Budget': num, 'Threshold': threshold}, 
                            ignore_index=True)
            
            print(probabilities)
            # sys.exit()
            sns.lineplot(x='Budget', y='Probability', hue='Threshold', data=probabilities, palette=sns.color_palette("Set1", 3))
            plt.ylabel('Pick Probability')
            plt.title(title)
            plt.savefig('plots/pick_prob/'+metric+'/' +title+ '.pdf', bbox_inches = "tight")
            # plt.show()

            for runtime in runtimes:
                runtime.append(title)
                all_runtimes.append(runtime)
            
            
            plt.figure()
            sns.heatmap(df_norm,  cbar_kws={'label': 'Norm. Exec. '+ metric}, linewidths=.5, linecolor="green", \
                        cmap=sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark"))
            plt.xticks(rotation=45)
            plt.xlabel('Instance Type')
            plt.ylabel('Number of Nodes')
            # plt.savefig('plots/data/pdf_'+ title + '.pdf', bbox_inches = "tight")
            # plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})
            plt.savefig('plots/heatmaps/'+metric+'/' +title+ '.pdf', bbox_inches = "tight")
            # plt.show()
            # sys.exit()