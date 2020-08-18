import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogsAll, getBest, prices, getAll, transform_labels
import sys
import numpy as np
import os


sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

config = json.load(open(configJsonName, 'r'))
prefix = config["prefix"]
log_dir = config["log_dir"]
value_key = config["value_key"]
metric = config["metric"]

count = 0
flag = True
if flag:
    config = json.load(open(configJsonName, 'r'))
    count = 0
    violations = pd.DataFrame(columns=['Algorithms', 'Threshold', "Violations"])
    for system in config["systems"]:
        for app in config["applications"][system]:
            for datasize in config["datasizes"]:
                count += 1
                # plt.figure() 
                title = system+"_"+app+"_"+datasize

                runtimes = getAll(app, system, datasize, dataset=config["dataset"])
                if len(runtimes) == 0:
                    continue
                df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
                df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
                # df["Cost"] = (prices[df["Type"] + "." + df["Size"]]/3600.0) * df["Num"] * df["Runtime"] 
                min_runtime = df['Runtime'].min()
                min_cost = df["Cost"].min()
                if "Runtime" in metric:
                    min_value = min_runtime 
                else:
                    min_value = min_cost

                runtimes = parseLogsAll(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
                df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Runtime', 'Experiment', 'Type', 'Size', 'Num', 'Completed'])
                # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])
                print(df)

                thresholds = [1.5, 2.0, 2.5]
                # min_value = best = getBest(app, system, datasize, dataset=config["dataset"])

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
    dir = 'plots/violations/' + prefix +"/"
    os.makedirs(dir, exist_ok=True) 
    v.to_csv(dir + 'violations.csv')

else:
    dir = 'plots/violations/' + prefix +"/"
    v = pd.read_csv(dir + 'violations.csv')

print(count)
v['Violations'] = v['Violations']/count
v = v[v['Algorithms']!='LHS']
plt.figure(figsize=(4, 2))            
ax = sns.barplot(x='Threshold', y='Violations', hue='Algorithms', data=v)

# plt.xticks(ax.get_xticks(), labels)

h, l = ax.get_legend_handles_labels()
legends = transform_labels(l)
# plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=4, prop={'size': 9}, handles=h, labels=legends)

ax.legend().set_visible(False)
if "Runtime" in metric:
    plt.xlabel("Normalized Exec. Time Threshold")
plt.ylabel("Avg. Violations")

dir = 'plots/violations/' + prefix +"/"
plt.savefig(dir + 'aggregate'+ '.pdf', bbox_inches = "tight")
plt.close()
# plt.show()

legendfig = plt.figure()
axi = legendfig.add_subplot(111)
if config["legends_outside"]:
    # axi.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=8, prop={'size': 9}, handles=h, labels=legends)
    l = axi.legend( prop={'size': 9}, ncol=8, handles=h, labels=legends)
else:
    axi.legend(loc='upper right',  ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
axi.xaxis.set_visible(False)
axi.yaxis.set_visible(False)
plt.gca().set_axis_off()

fig  = l.figure
fig.canvas.draw()
bbox  = l.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
plt.savefig('plots/violations/'+ prefix +"/"+'legend.pdf', bbox_inches=bbox)

plt.close()