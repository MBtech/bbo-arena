import pandas as pd 
import sys
import seaborn as sns
import json
import matplotlib.pyplot as plt 
import os 
import numpy as np 
from utils import transform_labels
from scipy import stats

plt.rcParams.update({'font.size': 16})

# sns.set(style="whitegrid")

configJsonName = sys.argv[1]

error_metrics = ['ae', 'mae', 'rmse']
config = json.load(open(configJsonName, 'r'))
prefix = config["prefix"]
metric = config["metric"]
error_df = pd.DataFrame()

print(metric)
for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            # plt.figure(figsize=(4,2.5))
            plt.figure()
            title = system+"_"+app+"_"+datasize
            print(title)
            if 'spark_rf_gigantic' in title:
                continue
            df = pd.read_csv('../algorithms/error/'+ metric +'_error_'+ title + '.csv')
            df.drop(columns=['mse'])
            df.loc[df['algorithm'] == 'baseline', 'algorithm'] = 'BL'

            sdf = pd.DataFrame()
            best_algo = "BL"
            for e in error_metrics:
                X = df.loc[df['algorithm'] == best_algo, e].to_numpy()
                sdf = sdf.append({'algorithm': best_algo, 'Error': np.mean(X), 'metric': e}, ignore_index=True)
                for algo in df['algorithm'].unique():
                    if algo in best_algo:
                        continue
                    Y = df.loc[df['algorithm'] == algo, e].to_numpy()
                    p_value = stats.ttest_ind(X,Y).pvalue
                    # print(p_value)
                    if p_value <= 0.05:
                        sdf = sdf.append({'algorithm': algo, 'Error': np.mean(Y), 'metric': e}, ignore_index=True)
                    else:
                        sdf = sdf.append({'algorithm': algo, 'Error': np.mean(X), 'metric': e}, ignore_index=True)
                        # print(algo, better)
            print(sdf)
            df = pd.melt(df, id_vars=['algorithm'], value_vars=['ae', 'mae', 'rmse'], var_name='metric')
            # print(df.groupby(['algorithm', 'metric']).mean().reset_index())
            # error_df = error_df.append(df.groupby(['algorithm', 'metric']).mean().reset_index())
            error_df = error_df.append(sdf)
            # ax= sns.boxplot(x="metric",y='value', hue='algorithm', data=df, showfliers=True)
            ax= sns.barplot(x="metric",y='Error', hue='algorithm', data=sdf)

            h, l = ax.get_legend_handles_labels()
            ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=3, prop={'size': 9}, handles=h, labels=transform_labels(l))
            # ax = sns.violinplot(y='rmse', x="algorithm", data=df, cut=0)
            # print(df.groupby(['algorithm']).describe())


            # xlabels = transform_labels([x.get_text() for x in ax.get_xticklabels()])
            # ax.set_xticklabels(xlabels)
            # plt.title(title)
            # plt.ylabel(error.upper())
            plt.xlabel('Error Metric')
            plt.savefig('plots/error/'+metric+'_error_'+ title + '.pdf', bbox_inches = "tight")
            plt.close()

            

plt.figure(figsize=(4,2.5))
# plt.figure()
ax= sns.boxplot(x="metric",y='Error', hue='algorithm', data=error_df, showfliers=False)
# ax = sns.violinplot(y='rmse', x="algorithm", data=df, cut=0)
# print(error_df[[error, "algorithm"]].groupby(['algorithm']).describe())
# ax.set_xticklabels(labels)

# xlabels = transform_labels([x.get_text() for x in ax.get_xticklabels()])
# ax.set_xticklabels(xlabels)

if "Runtime" not in metric:
    ax.set_yscale('log')

# ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=3, prop={'size': 9}, handles=h, labels=[e.upper() for e in error_metrics])
# ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=3, prop={'size': 9}, handles=h, labels=transform_labels(l))
ax.legend().set_visible(False)
plt.xlabel('Error Metric')
dir = 'plots/error/' + prefix +"/"
os.makedirs(dir, exist_ok=True)
plt.savefig(dir+prefix+'_error.pdf', bbox_inches = "tight")
plt.close()


legendfig = plt.figure()
axi = legendfig.add_subplot(111)
legends = transform_labels(l)
l = axi.legend( prop={'size': 11}, ncol=5, handles=h, labels=legends)
axi.xaxis.set_visible(False)
axi.yaxis.set_visible(False)
plt.gca().set_axis_off()

fig  = l.figure
fig.canvas.draw()
bbox  = l.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
plt.savefig('plots/error/legend.pdf', bbox_inches=bbox)

plt.close()