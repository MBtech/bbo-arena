import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from utils import getAll
import sys
import numpy as np

def total_cpu(row):
    num, size = row['Num'], row['Size']
    cpus = num * cpu[size]
    return cpus 

def total_memory(row):
    num, type, cpus = row['Num'], row['Type'], row['CPUs']
    memory = num * cpus * mem[type]
    return memory


cpu = {'large': 2, 'xlarge': 4, '2xlarge': 8}
mem = {'c4':2 , 'r4': 8, 'm4': 4}

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "opt"


config = json.load(open(configJsonName, 'r'))
count = 0
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            fig = plt.figure()
            title = system+"_"+app+"_"+datasize

            runtimes = getAll(app, system, datasize)
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            pd.set_option('display.max_rows', None)
            
            df['CPUs'] = df.apply(total_cpu, axis=1)
            df['Memory'] = df.apply(total_memory, axis=1)
            df['Family'] = df['Type'] +'.'+ df['Size']
            print(df.to_string)
        

            # ax = fig.gca(projection='3d')

            # surf=ax.plot_trisurf(df['CPUs'], df['Memory'], df['Runtime'], linewidth=0.2)

            # surf=ax.scatter(df['CPUs'], df['Memory'], df['Runtime'], c=df['Runtime'], s=60, cmap='cividis')

            # ax.set_zlabel('Runtime (s)')
            
            # ax = plt.scatter(x=df["CPUs"], y=df["Memory"],c=df["Runtime"]/df["Runtime"].min(), s=20, cmap="Spectral") 
            filled_markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
            ax = sns.scatterplot(x="Family", y="Num", hue=df["Runtime"]/df["Runtime"].min(), markers=filled_markers, 
                                     data=df)

            # cbar = plt.colorbar(ax)
            # cbar.set_label('Normalized Runtime', rotation=270 ,labelpad=15)

            plt.xlabel('Family')
            plt.ylabel('Num of nodes')
            idmin = df["Runtime"].idxmin()
            
            plt.plot([df.iloc[idmin]["Family"]], [df.iloc[idmin]["Num"]], 'X', markersize=10,color="black") 
            # sns.jointplot(x="CPUs", y="Memory", size="Runtime", data=df, kind='scatter')

            # fig.colorbar( surf, shrink=0.5, aspect=5)
            # plt.show()


            plt.title(title)
            plt.legend(loc='upper right', ncol=1, prop={'size': 7})
            plt.xticks(rotation=45)
            plt.savefig('plots/resources/'+ title + '.pdf', bbox_inches = "tight")

            # plt.show()
