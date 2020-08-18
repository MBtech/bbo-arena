import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest, getAll, prices
from utils import transform_labels as tl 
import sys 
import numpy as np
import os
from scipy import stats

def transform_labels(labels):
    transformed_labels = []
    for label in labels:
        if "BO" in label.get_text():
            transformed_label = label.get_text().split('_')[-2] + '(' + label.get_text().split('_')[-1] + ')'
        elif "HC" in label.get_text():
            transformed_label = "SHC"
        else:
            transformed_label = label.get_text().split('_')[0]

        transformed_labels.append(transformed_label)
    return transformed_labels

plt.rcParams.update({'font.size': 11})
steps = [6, 12, 18, 24, 30]
# steps = [9, 15, 21, 30]
percentiles = [0.5, 0.95]
# sns.set(style="whitegrid")

if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

print(configJsonName)
pd.set_option('display.max_rows', None)
config = json.load(open(configJsonName, 'r'))
prefix = config["prefix"]
scores = dict()
log_dir = config["log_dir"]
value_key = config["value_key"]

# Make sure that the index name is correct for bo case 
algos = list()
for algo in config['bbo_algos']:
    if 'bo1' in algo:
        for estimator in config["bo_estimators"]:
            for acq_method in config["bo_acq"][estimator]:
            
                algos.append((algo + '_' + estimator + '_' + acq_method).upper())
    else:
        algos.append(algo.upper())

print(algos)

scores = pd.DataFrame({ 'Algorithms': np.tile(np.repeat(algos, len(percentiles)), len(steps)), 'Score': [0.0]*len(algos)*len(steps)*len(percentiles), 
                    'Budget': np.repeat(steps, len(algos)*len(percentiles) ), 'Percentile': np.tile(percentiles, len(algos)*len(steps) )
                    }).set_index(['Algorithms', 'Budget', 'Percentile'])

slowdown_scores = pd.DataFrame({ 'Algorithms':[], 'Norm. Best Runtime': [], 'Budget': [], 'Percentile': []})

significance_test = pd.DataFrame({'benchmark': [], 'algorithm':[], 'best algo': [], 'statistic': [],'pvalue' : [], 
                                        'budget': [], 'test-name': []})




for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:

            # plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = getAll(app, system, datasize, dataset=config["dataset"])
            if len(runtimes) == 0:
                continue
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            # df["Cost"] = (prices[df["Type"] + "." + df["Size"]]/3600.0) * df["Num"] * df["Runtime"] 
            min_runtime = df['Runtime'].min()
            min_cost = df["Cost"].min()

            runtimes = parseLogs(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            df_select = df[df['Budget'].isin(steps)]
            df_select['Algorithms'] = df_select['Algorithms'].str.upper()
            # print(df_select)
            
            # Calculate statistical significance
            for budget in steps:
                for best_algo in algos:
                    for algo in algos[algos.index(best_algo):]:

                        if algo in best_algo:
                            continue

                        X = df_select[(df_select["Algorithms"]==best_algo) & (df_select["Budget"]==budget)]['Best Runtime']
                        Y = df_select[(df_select["Algorithms"]==algo) & (df_select["Budget"]==budget) ]['Best Runtime']
                        # print(best_algo, algo)
                        # print(len(X), len(Y))
                        try:
                            p_value = stats.wilcoxon(X,Y).pvalue
                            # print(p_value)
                            if p_value <= 0.05:
                                better = best_algo if np.median(X) < np.median(Y) else algo

                                significance_test = significance_test.append({'benchmark': title, 'algorithm': algo, 'best algo': best_algo, 
                                        'statistic': stats.ranksums(X,Y).statistic, 
                                        'pvalue': p_value, 'budget': budget, 'test-name': 'wilcoxon', 'better': better}, ignore_index=True)
                        except:
                            continue
                        
                        p_value = stats.ttest_ind(X,Y).pvalue
                        # print(p_value)
                        if p_value <= 0.05:
                            better = best_algo if np.mean(X) < np.mean(Y) else algo 

                            significance_test = significance_test.append({'benchmark': title, 'algorithm': algo, 'best algo': best_algo, 
                                    'statistic': stats.ttest_ind(X,Y).statistic, 
                                    'pvalue': stats.ttest_ind(X,Y).pvalue, 'budget': budget, 'test-name': 't-test', 'better': better}, ignore_index=True)
            
            
fig, ax = plt.subplots()

ttest_score = significance_test[significance_test['test-name']=='t-test']['better'].value_counts().nlargest(10).sort_values()
best_algo = ttest_score.reset_index().iloc[-1]['index']

ttest_score.plot(kind='bar') 
# print(ttest_score.reset_index().iloc[-1]['index'])
dir = 'plots/scores/' + prefix +"/"
os.makedirs(dir, exist_ok=True)
plt.tick_params(axis='both', which='minor', labelsize=8)

labels = transform_labels(ax.get_xticklabels())
plt.xticks(ax.get_xticks(), labels, rotation = 45)
plt.ylabel('Performance Score')
plt.savefig(dir + 't-test-hist.pdf', bbox_inches = "tight")
plt.close()

# plt.show()


significance_result = pd.DataFrame({'benchmark': [], 'algorithm':[], 'budget': [], 'performance': []})
best_algo_normalized = pd.DataFrame({'benchmark': [], 'budget': [], 'norm. perf': []})


for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:

            # plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize
            print(title)

            runtimes = getAll(app, system, datasize, dataset=config["dataset"])
            if len(runtimes) == 0:
                continue
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
            # df["Cost"] = (prices[df["Type"] + "." + df["Size"]]/3600.0) * df["Num"] * df["Runtime"] 
            min_runtime = df['Runtime'].min()
            min_cost = df["Cost"].min()

            runtimes = parseLogs(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            df_select = df[df['Budget'].isin(steps)]
            df_select['Algorithms'] = df_select['Algorithms'].str.upper()
            # print(df_select)
            
            # Calculate statistical significance
            i = 0
            for budget in steps:
                for algo in algos:

                    if algo in best_algo:
                        continue

                    X = df_select[(df_select["Algorithms"]==best_algo) & (df_select["Budget"]==budget)]['Best Runtime']
                    Y = df_select[(df_select["Algorithms"]==algo) & (df_select["Budget"]==budget) ]['Best Runtime']
                    
                    p_value = stats.ttest_ind(X,Y).pvalue
                    # print(p_value)

                    if "Exec. Cost" in config["metric"]:
                        norm_factor = min_cost
                    else:
                        norm_factor = min_runtime   

                    val = 1.0
                    if p_value <= 0.05:
                        # better = best_algo if np.mean(X) < np.mean(Y) else algo 
                        val = np.mean(Y)/np.mean(X) 
                    
                    if "BO" in algo:
                        algo = algo.split('_')[-2] + '(' + algo.split('_')[-1] + ')'
                    else:
                        algo = algo.split('_')[0]
                    significance_result = significance_result.append({'benchmark': title, 'algorithm': algo, 
                                    'budget': int(budget), 'performance': val}, ignore_index=True)
                    

                    best_algo_normalized = best_algo_normalized.append({'benchmark': title, 'budget': int(i),
                                     'norm. perf': np.mean(X)/norm_factor}, ignore_index=True)
                i +=1 
print(significance_result)

fig, ax1 = plt.subplots(figsize=(4,2.5))
ax1= sns.barplot(x='budget', y='performance', hue='algorithm', data=significance_result)
plt.axhline(y=1.0)
ax1.set_xticklabels(steps)
ax1.set_ylim([0.9, 1.3])
ax1.set_ylabel('Norm. Perf w.r.t. ' + best_algo.split('_')[-2] + '(' + best_algo.split('_')[-1] + ')')
h, l = ax1.get_legend_handles_labels()

# if config["legends_outside"]:
#     ax1.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
#     # l = axi.legend(ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
# else:
#     ax1.legend(loc='upper right',  ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
labels = tl(l)
if len(labels) > 4:
    ax1.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=3, prop={'size': 9}, handles=h, labels=labels)
else:
    ax1.legend(loc='upper right',  ncol=2, prop={'size': 9}, handles=h, labels=labels)

# print(best_algo_normalized)
# ax2 = ax1.twinx()
# ax2.set_ylim([1.0, 1.5])
# sns.lineplot(x='budget', y='norm. perf', color='black', marker="o", ci=None, data=best_algo_normalized, ax=ax2)
# ax2.set_ylabel('Norm. Perf w.r.t. Best Conf.')

dir = 'plots/scores/' + prefix +"/"

os.makedirs(dir, exist_ok=True)
fig.savefig(dir + 'perf.pdf', bbox_inches = "tight")
plt.close()

## Separate Legends plot
# legendfig = plt.figure()
# axi = legendfig.add_subplot(111)
# if config["legends_outside"]:
#     axi.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
#     # l = axi.legend(ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
# else:
#     axi.legend(loc='upper right',  ncol=config["legend_cols"], prop={'size': 9}, handles=h, labels=l)
# axi.xaxis.set_visible(False)
# axi.yaxis.set_visible(False)
# plt.gca().set_axis_off()

# fig  = l.figure
# fig.canvas.draw()
# bbox  = l.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
# plt.savefig('plots/scores/legend.pdf', bbox_inches=bbox)

# plt.close()