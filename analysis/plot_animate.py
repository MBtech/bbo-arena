import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import getAll
import sys
import numpy as np
import math
import matplotlib.animation as animation

# def animate(i):
#     cmap1 = mpl.colors.ListedColormap(['c'])
#     sns.heatmap(df_norm, mask=df_norm[''], cmap=cmap1, cbar=False)

#     for c in scatters:
#         # do whatever do get the new data to plot
#         x = np.random.random(size=(50,1))*50
#         y = np.random.random(size=(50,1))*10
#         xy = np.hstack([x,y])
#         # update PathCollection offsets
#         c.set_offsets(xy)
#     txt.set_text('frame={:d}'.format(i))
#     return scatters+[txt]

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

            runtimes = getAll(app, system, datasize, metric=metric, dataset=config["dataset"])
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            
            # df = df[df["Num"].isin(num_of_nodes)]
            df["Family"] = df['Type'] + '.'+df['Size']
            df.drop(['Type', 'Size'], axis=1, inplace=True)
            df_norm = df.copy()
            df_norm['Runtime'] =  df['Runtime']/df['Runtime'].min()
            df_norm['Runtime'] = df_norm['Runtime']#.clip(0, 2)
            df_norm = df_norm.pivot("Num", "Family", "Runtime")
            df_norm = df_norm.reindex(['c4.large', 'c4.xlarge', 'c4.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 'r4.large', 'r4.xlarge', 'r4.2xlarge'], axis=1)
            print(df_norm)


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