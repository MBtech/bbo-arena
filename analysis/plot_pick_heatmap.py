import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import *
import sys
import numpy as np
import math

pd.set_option('display.max_columns', 500)
sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

plt.rcParams.update({'font.size': 12})

config = json.load(open(configJsonName, 'r'))
count = 0
good_confs = list()
all_runtimes = list()
metric = sys.argv[2]
clip= 5

dividers = {'large': 8, 'xlarge': 4, '2xlarge': 2, '4xlarge': 1}
indices = []
for t in types[config["dataset"]]:
    for s in sizes[config["dataset"]]:
        indices.append(t+'.'+s)

algos = list()
for algo in config['bbo_algos']:
    if 'bo1' in algo:
        for estimator in config["bo_estimators"]:
            for acq_method in config["bo_acq"][estimator]:
            
                algos.append((algo + '_' + estimator + '_' + acq_method))
    else:
        algos.append(algo)

coverage = pd.DataFrame()
# coverage['Algorithms'] = algos 

benchmark = 'spark1.5_kmeans_bigdata'
families_explored = list()
# benchmark = ''
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            
            title = system+"_"+app+"_"+datasize
            print(title)

            if benchmark not in title:
                continue

            runtimes = getAll(app, system, datasize, metric=metric, dataset=config["dataset"])
            if len(runtimes) == 0:
                continue

            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            
            if config["dataset"] == "l":
                df["Num"] = df.apply(lambda x: (x["Num"] / dividers[x["Size"]]), axis=1)

            df["Family"] = df['Type'] + '.'+df['Size']
            df.drop(['Type', 'Size'], axis=1, inplace=True)
            df_norm = df.copy()
            df_norm["Num"] = df_norm["Num"].astype(int)
            print(df[df['Runtime'] == df['Runtime'].min()])
            df_norm['Runtime'] =  df['Runtime']/df['Runtime'].min()
            df_norm['Runtime'] = df_norm['Runtime'].clip(0, clip)
            # print(df_norm)
            df_norm = df_norm.pivot("Num", "Family", "Runtime")
            # df_norm = df_norm.reindex(['c5.large', 'c5.xlarge', 'c5.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 
            #                                 'r4.large', 'r4.xlarge', 'r4.2xlarge'], axis=1)

            df_norm = df_norm.reindex(indices, axis=1)
            # print(df_norm)
            total_rows=len(df_norm.axes[0])
            total_cols=len(df_norm.axes[1])  
            
            
            runtimes = parseLogsAll(system, app, datasize, configJsonName, config['log_dir'], config['value_key'])
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num', 'Completed'])

            print(df)
            if config["dataset"] == "l":
                df["Num"] = df.apply(lambda x: (x["Num"] / dividers[x["Size"]]), axis=1)

            coverage['Algorithms'] = df['Algorithms'].unique()
            coverage[title] = df.drop_duplicates(['Algorithms', 'Type', 'Size', 'Num']).groupby(['Algorithms']).size().reset_index(name=title)[title]
            # continue
            for algo in algos:
                print(algo)
                
                labels = np.full((total_rows, total_cols), "", dtype=object)
                # labels = np.empty([total_rows, total_cols], dtype=object)
                # labels = np.array([[""]*total_cols]*total_rows)
                # ax.invert_yaxis()
                max_budget = 30
                exp_no = 10
                
                
                for exp_no in range(0, 50):
                    family_set = set()
                    for i in range(1, max_budget+1):
                        point = df[(df['Algorithms']==algo) & (df['Experiment']==exp_no) & (df['Budget']==i)]
                        # print(point)
                        t = point['Type'].iloc[0]
                        s = point['Size'].iloc[0]
                        index = indices.index(t+'.'+s)
                        # print(t + '.' + s, point['Num'].iloc[0])
                        # print(point['Num'])
                        
                        if config["dataset"] == "l":
                            row = int(point['Num'].iloc[0])-2
                            # row = -(row + 1)
                            labels[row][index] = str(i)
                            # 
                        else:
                            row = number_of_nodes[config["dataset"]][s].index(int(point['Num'].iloc[0]))
                            # Fix because of some missing data in the Scout dataset
                            if row >= 6 and s in 'large':
                                row = row+1
                            labels[row][index] = str(i)      

                        # if i <= 3:
                        #     continue
                        family_set.add(t)
                        families_explored.append([algo, title, i, len(family_set)])

                        # print(row, index)

                print(df[(df['Algorithms']==algo) & (df['Experiment']==exp_no) & (df['Completed']==True) & (df['Budget'] <=max_budget)]['Runtime'].min())
                                  
                # print(labels)
                df_new = df[df['Algorithms']==algo][['Runtime', 'Type', 'Size', 'Num']]
                df_new["Family"] = df_new['Type'] + '.'+df_new['Size']
                df_new.drop(['Type', 'Size'], axis=1, inplace=True)
                count_df = df_new.groupby(['Family', 'Num']).size()
                
                df_new = count_df.to_frame(name = 'Size').reset_index()
                df_new = df_new.pivot("Num", "Family", "Size")
                df_new = df_new.reindex(indices, axis=1)
                # print(df_new)

            #     plt.figure(figsize=(4, 3))
            #    # ax = sns.heatmap(df_new,  cbar_kws={'label': 'Count'}, linewidths=.5, linecolor="green", \
            #    #         cmap=sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark"))
            #     ax = sns.heatmap(df_norm,  cbar_kws={'label': 'Norm. Exec. Cost'}, linewidths=.5, linecolor="green", \
            #                 cmap=sns.diverging_palette(250, 15, s=75, l=40, n=9, center="dark"), annot=labels, fmt="", 
            #                 annot_kws={"color": 'yellow', "weight":'bold', 'size': 9})

            #     cbar = ax.collections[0].colorbar
            #     labels = [item.get_text() for item in cbar.ax.get_yticklabels()]
            #     labels[-1] = '$\geq$' + str(clip)
            #     cbar.ax.set_yticklabels(labels)
            #     # ax.invert_yaxis()
            #     # plt.title(algo)
            #     ax.tick_params(axis='x', which='major', labelsize=9)
            #     plt.xticks(rotation=90)
            #     plt.xlabel('Instance Type')
            #     if config["dataset"] == "l":
            #         plt.ylabel('Cluster Size')
            #     else:
            #         plt.ylabel('Number of Instances')
            # # plt.savefig('plots/data/pdf_'+ title + '.pdf', bbox_inches = "tight")
            # # plt.title(title)
            # # plt.legend(loc='upper right', ncol=2, prop={'size': 9})

            #     dir = 'plots/pick-heatmaps/'
            #     os.makedirs(dir+metric+'/'+algo, exist_ok=True)
            #     plt.savefig(dir+metric+'/' +algo + '/'+title+ '.pdf', bbox_inches = "tight")
            
            # plt.show()
            # sys.exit()

fig = plt.figure(figsize=(3.5, 2))
df = pd.DataFrame(families_explored, columns = ['Algorithm', 'Workload', 'Budget', 'Families tested'])
print(df)
ax = sns.lineplot(data=df, x='Budget', hue='Algorithm', y='Families tested', ci=None)
ax.set_ylim(bottom=1)
ax.set_xticks(range(6, 36, 6))
ax.set_yticks(range(1, len(types[config["dataset"]])+1))
plt.ylabel('No. of Inst. Families')
h, l = ax.get_legend_handles_labels()
ax.legend(loc="lower right", ncol=2, prop={'size': 9}, handles=h[1:], labels=transform_labels(l[1:]))
dir = 'plots/pick-heatmaps/'
os.makedirs(dir+metric+'/'+algo, exist_ok=True)
# plt.savefig(dir+metric+'/'+ config["dataset"]+'_explored.pdf', bbox_inches = "tight")

plt.show()
# print(coverage)