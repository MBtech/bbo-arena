import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest
import sys 
import numpy as np

steps = [6, 12, 18, 24, 30]
percentiles = [0.05,0.5, 0.95]
sns.set(style="whitegrid")

if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "best"

pd.set_option('display.max_rows', None)
config = json.load(open(configJsonName, 'r'))

scores = dict()

# Make sure that the index name is correct for bo case 
algos = list()
for algo in config['bbo_algos']:
    if 'bo' in algo:
        for estimator in config["bo_estimators"]:
            for acq_method in config["bo_acq"][estimator]:
            
                algos.append((algo + '_' + estimator + '_' + acq_method).upper())
    else:
        algos.append(algo.upper())

# for step in s teps:
scores = pd.DataFrame({ 'Algorithms': np.tile(np.repeat(algos, len(percentiles)), len(steps)), 'Score': [0.0]*len(algos)*len(steps)*len(percentiles), 
                    'Budget': np.repeat(steps, len(algos)*len(percentiles) ), 'Percentile': np.tile(percentiles, len(algos)*len(steps) )
                    }).set_index(['Algorithms', 'Budget', 'Percentile'])

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure(figsize=(5,3))
            title = system+"_"+app+"_"+datasize

            runtimes = parseLogs(system, app, datasize, configJsonName)
            df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
            df_select = df[df['Budget'].isin(steps)]
            df_select['Algorithms'] = df_select['Algorithms'].str.upper()
            # print(df_select)

            total_ranks = pd.DataFrame({'Algorithms':[], 'Budget':[], 'Score':[]})
            for budget in steps:

                df_grouped = df_select[df_select['Budget'] == budget].drop(['Budget', 'Experiment'], axis=1).groupby(['Algorithms']) #.describe(percentiles=[0.05, 0.5, 0.95])

                ranks = df_grouped.quantile(percentiles).rank(method='dense')#.reset_index()
                ranks['Budget'] = np.repeat(budget, len(algos)*3)
                ranks = ranks.reset_index()#.set_index(['Algorithms', 'Budget'])
                ranks = ranks.rename(columns={'Best Runtime': 'Score', 'level_1': 'Percentile'})
                # print(ranks)
                total_ranks = total_ranks.append(ranks)
                # print(total_ranks)
            total_ranks = total_ranks.set_index(['Algorithms', 'Budget', 'Percentile'])

            # print(total_ranks)
            # print(scores)
            scores +=  total_ranks

            # print(scores+ranks)
                # print(scores[scores['Budget']==budget]['Score'])
                # for t, frame in df_grouped:
                #     stats = frame.describe(percentiles=[0.05, 0.5, 0.95])
                #     print(stats)
                #     print(stats.rank())
                #     # statistics['5%']
                #     print(stats.loc['5%', 'Best Runtime'])
                #     print(stats.loc['50%', 'Best Runtime'])
                    
            
            # stats = df.groupby(['Algo', 'Budget'])['Runtime'].agg(['mean', 'count', 'std'])

            sns.boxplot(x='Budget', y='Best Runtime', hue="Algorithms", data=df_select, showfliers=False)
            # sns.violinplot(x='Budget', y='Best Runtime', hue="Algorithms", data=df_select, cut=0)

            best = getBest(app, system, datasize)
            plt.axhline(best, color='blue')
            # plt.ylim(0, 2400)
            # plt.title(title)
            plt.legend(loc='upper right', ncol=3, prop={'size': 7})
            plt.savefig('plots/'+prefix+'_'+ title + '.pdf', bbox_inches = "tight")
            # plt.show()
print(scores)
scores = scores.reset_index()
for p in percentiles:
    plt.figure(figsize=(4,2.5))
    sns.barplot(x='Budget', y='Score', hue='Algorithms', data=scores[scores['Percentile']==p])
    plt.legend(loc='upper right', ncol=2, prop={'size': 8})
    # plt.title('Percentile='+str(p))
    plt.savefig('plots/scores/'+prefix+'_'+ 'Percentile_'+str(p) + '.pdf', bbox_inches = "tight")
    # plt.show()

overall_score = scores.groupby(['Algorithms', 'Budget'])['Score'].sum().reset_index()
plt.figure(figsize=(4,2.5))
sns.barplot(x='Budget', y='Score', hue='Algorithms', data=overall_score)
plt.legend(loc='upper right', ncol=2, prop={'size': 7})
plt.savefig('plots/scores/'+prefix+ '.pdf', bbox_inches = "tight")