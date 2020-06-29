import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogsAll, getBest
import sys
import numpy as np

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "opt"

flag = False
if flag:
    config = json.load(open(configJsonName, 'r'))
    count = 0
    violations = pd.DataFrame(columns=['Algorithms', 'Threshold', "Violations"])
    for system in config["systems"]:
        for app in config["applications"][system]:
            for datasize in config["datasizes"]:
                # plt.figure() 
                title = system+"_"+app+"_"+datasize

                runtimes = parseLogsAll(system, app, datasize, configJsonName)
                
                df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num'])
                # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])
                # print(df)

                thresholds = [1.5, 2.0, 2.5]
                min_value = best = getBest(app, system, datasize, dataset=config["dataset"])

                for algo in df['Algorithms'].unique():
                    print(algo)
                
                    for threshold in thresholds:
                        n_violations = []
                        for experiment_no in df['Experiment'].unique():
                            n_violations.append(len( df[(df["Algorithms"]==algo) & (df["Experiment"]==experiment_no) & \
                                (df["Runtime"] > threshold*min_value) & (df["Budget"] > 3) ] ) )
                        violations = violations.append({'Algorithms': algo.upper(), 'Threshold': threshold, 'Violations': np.median(n_violations)}, ignore_index=True )
            
                # print(violations)
                # sns.relplot(x='Budget', y='Runtime', hue="Algorithms", ci="sd", data=df, kind="line")
                # plt.axhline(best, color='black')
                # plt.xlim(0, 30)
                # plt.title(title)
                # plt.legend(loc='upper right', ncol=2, prop={'size': 9})
                # plt.savefig('plots/violations/'+prefix+'_'+ title + '.pdf')
                count +=1

    v = violations.groupby(['Algorithms', 'Threshold']).sum()
    v = v.reset_index()
    v.to_csv('plots/violations/violations.csv')

else:
    v = pd.read_csv('plots/violations/violations.csv')

v['Violations'] = v['Violations']/18.0
v = v[v['Algorithms']!='LHS']
plt.figure(figsize=(5, 2.5))            
ax = sns.barplot(x='Threshold', y='Violations', hue='Algorithms', data=v)
h, l = ax.get_legend_handles_labels()

plt.xlabel("Normalized Runtime Threshold")
plt.ylabel("Avg. Violations")
legends = ['BO(ET)', 'BO(GBRT)', 'BO(GP)', 'BO(RF)', 'SHC', 'RANDOM', 'SA', 'TPE']
plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=4, prop={'size': 9}, handles=h, labels=legends)
plt.savefig('plots/violations/aggregate'+ '.pdf', bbox_inches = "tight")

plt.show()
