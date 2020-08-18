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

plt.rcParams.update({'font.size': 12})
# plt.rc('ytick', labelsize=9)

config = json.load(open(configJsonName, 'r'))
count = 0
good_confs = list()
all_runtimes = list()
num_of_nodes = [4, 6, 8, 10, 12]
metric = sys.argv[2]
label = sys.argv[3]
clip = 2

dividers = {'large': 8, 'xlarge': 4, '2xlarge': 2, '4xlarge': 1}

indices = []
for t in types[config["dataset"]]:
    for s in sizes[config["dataset"]]:
        indices.append(t+'.'+s)

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = getAll(app, system, datasize, metric=metric, dataset=config["dataset"])
            # print(runtimes)
            if len(runtimes) == 0:
                continue

            plt.figure()
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            
            if config["dataset"] == "l":
                df["Num"] = df.apply(lambda x: (x["Num"] / dividers[x["Size"]]), axis=1)
            
            # Uncomment this line for a uniform small heatmap
            # df = df[df["Num"].isin(num_of_nodes)]

            df["Family"] = df['Type'] + '.'+df['Size']
            df.drop(['Type', 'Size'], axis=1, inplace=True)
            df_norm = df.copy()
            df_norm["Num"] = df_norm["Num"].astype(int)
            df_norm['Runtime'] =  df['Runtime']/df['Runtime'].min()
            print(df['Runtime'].min())
            df_norm['Runtime'] = df_norm['Runtime'].clip(0, clip)
            df_norm = df_norm.pivot("Num", "Family", "Runtime")
            # df_norm = df_norm.reindex(['c5.large', 'c5.xlarge', 'c5.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 
            #                                 'r4.large', 'r4.xlarge', 'r4.2xlarge'], axis=1)

            df_norm = df_norm.reindex(indices, axis=1)
            # print(df_norm)

            max_runtime = df['Runtime'].max()
            r = max_runtime / df['Runtime'].min()
            # print(r)

            min_runtime = df['Runtime'].min()
            runtime_threashold = 1.1*min_runtime
            good_confs.append([title, len(df[df['Runtime']<=runtime_threashold])])

            # Measuring random pick probability
            thresholds = ['1.1', '1.2', '1.5']
            probabilities = pd.DataFrame({'Budget':[], 'Threshold': [], 'Probability': []})
            for threshold in thresholds:
                # print(threshold)
                prob = len(df[df['Runtime']<=min_runtime*float(threshold)])/len(df)
                for num in range(1, config["budget"]+1):
                    probabilities = probabilities.append({'Probability': (1 - (1 - prob)**num ), 'Budget': num, 'Threshold': threshold}, 
                            ignore_index=True)
            
            # print(probabilities)
            # sys.exit()
            sns.lineplot(x='Budget', y='Probability', hue='Threshold', data=probabilities, palette=sns.color_palette("Set1", 3))
            plt.ylabel('Pick Probability')
            plt.title(title)

            plt.savefig('plots/pick_prob/'+metric+'/' +title+ '.pdf', bbox_inches = "tight")
            # plt.show()
            plt.close()

            for runtime in runtimes:
                runtime.append(title)
                all_runtimes.append(runtime)
            
            
            plt.figure(figsize=(4, 3))
            ax = sns.heatmap(df_norm,  cbar_kws={'label': 'Norm. Exec. '+ label}, linewidths=.5, linecolor="green", \
                        cmap=sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark"))

            cbar = ax.collections[0].colorbar
            labels = [item.get_text() for item in cbar.ax.get_yticklabels()]
            labels[-1] = '$\geq$' + str(clip)
            cbar.ax.set_yticklabels(labels)

            ax.tick_params(axis='both', which='major', labelsize=10, tick1On=True)
            plt.xticks(rotation=90)
            plt.xlabel('Instance Type')

            if config["dataset"] == "l":
                plt.ylabel('Cluster Size')
            else:
                plt.ylabel('Number of Instances')

            # plt.savefig('plots/data/pdf_'+ title + '.pdf', bbox_inches = "tight")
            # plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})

            plt.savefig('plots/heatmaps/'+metric+'/' +title+ '.pdf', bbox_inches = "tight")
            # plt.show()
            plt.close()
            # sys.exit()