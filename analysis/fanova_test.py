import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import parseLogs, getBest, getAll, prices
import sys 
import numpy as np
import itertools
import os
from scipy import stats
from fanova import fANOVA

def write_to_config(config, acq="EI", estimator="GP"):
    ## Write all the algorithm names to the config file
    config["bbo_algos"] = []
    for n in n_init:
        if "tpe" in algo or "bo" in algo:
            name = algo.split('_')[0] + '_' + str(n)
        else:
            name = algo + '_' + str(n)


        config["initial_samples"] = n
        # Generate permutation in the form of hyerparameter:value
        if "bo" in algo:
            keys, values = zip(*hyper_params[algo][acq].items())
            config["bo_estimators"] = [estimator]
            config["bo_acq"][estimator] = [acq]
        else:
            keys, values = zip(*hyper_params[algo].items())
        hyper_param_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
        # print(hyper_param_configs)
        for hyper_param_config in hyper_param_configs:
            algo_name = name
            for param in hyper_param_config:
                algo_name = algo_name + '_' + str(hyper_param_config[param]) 
                config[algo][param] = hyper_param_config[param]
            config["bbo_algos"].append(algo_name)
    print(config)
    json.dump(config, open(configJsonName, 'w'), indent=4)

def get_results():
    print(title)

    ## Block of code to fine min cost and min runtime
    runtimes = getAll(app, system, datasize, dataset=config["dataset"])
    if len(runtimes) == 0:
       return [[]], []
       
    df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
    df["Cost"] = df.apply(lambda x: (prices[x["Type"] + "." + x["Size"]]/3600.0) * x["Num"] * x["Runtime"] , axis=1)
    min_runtime = df['Runtime'].min()
    min_cost = df["Cost"].min()


    runtimes = parseLogs(system, app, datasize, configJsonName, logDir=log_dir, value_key=value_key)
    df = pd.DataFrame(runtimes, columns = ['Algorithms', 'Budget', 'Best Runtime', 'Experiment'])
    # print(df)
    df_select = df[df['Budget'].isin(steps)]
    df_select['Algorithms'] = df_select['Algorithms'].str.upper()
    df_select['Init Samples'] = df.apply(lambda x: int(x["Algorithms"].split("_")[1]), axis=1)


    norm_df = df_select.copy()
    if "Exec. Cost" in config["metric"]:
        norm_df['Norm. Best Runtime'] = norm_df['Best Runtime']/min_cost
    else:
        norm_df['Norm. Best Runtime'] = norm_df['Best Runtime']/min_runtime   


    plt.figure(figsize=(20,10))
    ax = sns.barplot(x='Budget', y='Norm. Best Runtime', hue='Algorithms', data=norm_df)# , dodge=0.5)
    # ax = sns.boxplot(x='Budget', y='Norm. Best Runtime', hue='Algorithms', data=norm_df)
    h, l = ax.get_legend_handles_labels()
    if config["legends_outside"]:
        ax.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower right", ncol=config["legend_cols"], prop={'size': 10})
    else:
        ax.legend(loc='upper right',  ncol=config["legend_cols"], prop={'size': 10})
    plt.ylim(bottom=1.0)
    plt.ylabel("Norm. Best " + config["metric"])
    dir = 'plots/norm/' + prefix +"/"
    os.makedirs(dir, exist_ok=True)
    plt.savefig(dir + title  + '.pdf', bbox_inches = "tight")
    plt.close()


    i = 2
    for e in params:
        df_select[e] =  df.apply(lambda x: float(x["Algorithms"].split("_")[i]), axis=1)
        i+=1
    X = df_select[["Budget", "Experiment", "Init Samples", *params]].values
    Y = df_select["Best Runtime"].values

    # calculate_significance(df_select, title)
    return X, Y



def calculate_significance(df_select, benchmark):
    global significance_test
    algos = list(df_select['Algorithms'].dropna().unique())
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

                        significance_test = significance_test.append({'benchmark': benchmark, 'algorithm': algo, 'best algo': best_algo, 
                                'statistic': stats.ranksums(X,Y).statistic, 
                                'pvalue': p_value, 'budget': budget, 'test-name': 'wilcoxon', 'better': better}, ignore_index=True)
                except:
                    continue
                
                p_value = stats.ttest_ind(X,Y).pvalue
                # print(p_value)
                if p_value <= 0.05:
                    better = best_algo if np.mean(X) < np.mean(Y) else algo 

                    significance_test = significance_test.append({'benchmark': benchmark, 'algorithm': algo, 'best algo': best_algo, 
                            'statistic': stats.ttest_ind(X,Y).statistic, 
                            'pvalue': stats.ttest_ind(X,Y).pvalue, 'budget': budget, 'test-name': 't-test', 'better': better}, ignore_index=True)
    
    # significance_test[significance_test['test-name']=='t-test']['better'].value_counts().sort_values().plot(kind='barh') 
    # dir = 'plots/norm/' + prefix +"/t-test-hist/"
    # os.makedirs(dir, exist_ok=True)
    # plt.savefig(dir + title  + '.pdf', bbox_inches = "tight")
    # plt.close()

    # significance_test[significance_test['test-name']=='wilcoxon']['better'].value_counts().sort_values().plot(kind='barh') 
    # dir = 'plots/norm/' + prefix +"/wilcoxon-hist/"
    # os.makedirs(dir, exist_ok=True)
    # plt.savefig(dir + title  + '.pdf', bbox_inches = "tight")
    # plt.close()
    # # print(significance_test)
    # significance_test.to_csv('plots/norm/'+ prefix +'/'+ title  + '.csv')


best_algos = {"hc": "HC_9_50",
                "sa": "SA_9_0.3_50",
                "tpe_args": "TPE_3_0.1",
                "bo_args_PI": "BO_3_0.1", 
                "bo_args_EI": "BO_3_0.1", 
                "bo_args_LCB": "BO_3_1.0", 
                "bo_args_gp_hedge": "BO_3_0.1_1.0", 
                }



estimators = {"hc": ["hc"],
              "sa": ["sa"],
              "tpe_args": ["tpe"],
              "bo_args": ["GP", "GBRT", "ET", "RF"] 
            }
acq_funcs= {
    "hc" : [""],
    "sa": [""],
    "tpe": [""],
    "RF": ["EI", "LCB", "PI"],
    "ET":  ["EI", "LCB", "PI"],
    "GBRT": ["EI", "LCB", "PI"],
    "GP":  ["EI", "LCB", "PI", "gp_hedge"]
      }

if len(sys.argv) == 3:
    algo = sys.argv[2]
    estimator = "GBRT"
    acq = "PI"

elif len(sys.argv)>3:
    algo = sys.argv[2]
    estimator = sys.argv[3]
    acq = sys.argv[4]
else:
    algo = "bo_args"
    estimator = "GBRT"
    acq = "PI"

if "bo" in algo:    
    ba = algo + "_" + estimator + "_" + acq
else:
    ba = best_algos[algo]


if "bo" in algo:    
    imp = algo + "_" + acq
else:
    imp = algo

hyper_params = {"hc": {"temp": [50, 100, 250, 500, 750, 1000]},
                "sa": {
                    "schedule_constant": [0.3, 0.5, 0.7, 0.9],
                    # "temp": [50, 100, 750, 1000]

                    "temp": [50, 100, 250, 500, 750, 1000]
                     },
                "tpe_args": {"gamma": [0.1, 0.25, 0.4, 0.55, 0.7]},
                "bo_args": { 
                    "EI": { "xi": [0.01, 0.05, 0.1, 0.2]}, 
                    "PI": { "xi": [0.01, 0.05, 0.1, 0.2]},
                    "LCB": {"kappa": [1.0, 1.5, 1.96, 3.0, 5.0]},
                    "gp_hedge": {"xi": [0.01, 0.05, 0.1, 0.2], "kappa": [1.0, 1.5, 1.96, 3.0, 5.0]}
                    }
                }

n_init = [3, 6, 9]

steps = [6, 12, 18, 24, 30]

significance_test = pd.DataFrame({'benchmark': [], 'algorithm':[], 'best algo': [], 'statistic': [],'pvalue' : [], 'budget': [], 'test-name': []})
# steps = [9, 15, 21, 30]
sns.set(style="whitegrid")

if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
else:
    configJsonName = "test_configs/all_runs.json"

print(configJsonName)
# pd.set_option('display.max_rows', None)
config = json.load(open(configJsonName, 'r'))
prefix = config["prefix"]
scores = dict()
log_dir = config["log_dir"]
value_key = config["value_key"]


# sys.exit()

# Make sure that the index name is correct for bo case 
# algos = list()
# for algo in config['bbo_algos']:
#     if 'bo' in algo:
#         for estimator in config["bo_estimators"]:
#             for acq_method in config["bo_acq"][estimator]:
            
#                 algos.append((algo + '_' + estimator + '_' + acq_method).upper())
#     else:
#         algos.append(algo.upper())

performance_data = pd.DataFrame({ 'Algorithms':[], 'Best Runtime': [], 'Budget': [], 'Percentile': []})

if "bo" in algo:
    params = list(hyper_params[algo][acq].keys())
else:
    params=list(hyper_params[algo].keys())

# write_to_config(config, acq="GP", estimator="PI")

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
        
        
            if "bo" in algo:
                title = system+"_"+app+"_"+datasize+"_"+estimator+"_"+acq
                write_to_config(config, acq=acq, estimator=estimator)
                X, Y = get_results()
                
            else:
                title = system+"_"+app+"_"+datasize
                write_to_config(config)
                X, Y = get_results()

            if len(X)==0 or len(Y)==0:
                continue 

            
            f = fANOVA(X,Y) 
            i = 0

            param_importance = []
            all_params = ["Budget", "Experiment", "Init Samples", *params]
            for e in all_params:
                importance = f.quantify_importance((i, ))
                param_importance.append([e, list(importance.values())[0]['individual importance']])
                # print(importance.values())
                print(e, importance)
                i +=1
            print(param_importance)

            ### Marginal Pairwise importance. Takes too long 
            # important_pairs = f.get_most_important_pairwise_marginals(n=3)
            # # print(list(important_pairs))
            # for pairs in list(important_pairs.keys()):
            #     # print(pairs)
            #     importance = important_pairs[pairs]
            #     index_param_0 = int(pairs[0].split('_')[-1])
            #     index_param_1 = int(pairs[0].split('_')[-1])
            #     pairs = (all_params[index_param_0], all_params[index_param_1])
            #     param_pairs = str(pairs)
            #     print(param_pairs)
            #     # print(important_pairs[pairs])
            #     param_importance.append([param_pairs, importance])


            df = pd.DataFrame(param_importance, columns = ['Params', 'Importance'])
            plt.figure()    
            ax = sns.barplot(x='Params', y='Importance',  data=df)
            ax.set_xticklabels(ax.get_xticklabels(), rotation = 45)
            dir = 'plots/importance/' + prefix +"/"
            os.makedirs(dir, exist_ok=True)
            plt.savefig(dir + title  + '.pdf', bbox_inches = "tight")
            plt.close()

            df.to_csv('plots/importance/'+ imp +'.csv', mode='a', header=False)

# significance_test = pd.read_csv('plots/norm/'+ prefix +'/'+ 'significance-test_' + ba +'.csv')


# significance_test[significance_test['test-name']=='t-test']['better'].value_counts().nlargest(10).sort_values().plot(kind='barh') 
# dir = 'plots/norm/' + prefix +"/"
# os.makedirs(dir, exist_ok=True)
# plt.tick_params(axis='both', which='minor', labelsize=8)
# plt.savefig(dir + 't-test-hist_' + ba + '.pdf', bbox_inches = "tight")
# plt.close()

# significance_test[significance_test['test-name']=='wilcoxon']['better'].value_counts().nlargest(10).sort_values().plot(kind='barh') 
# dir = 'plots/norm/' + prefix +"/"
# os.makedirs(dir, exist_ok=True)
# plt.tick_params(axis='both', which='minor', labelsize=8)
# plt.savefig(dir + 'wilcoxon-hist_' + ba +'.pdf', bbox_inches = "tight")
# plt.close()
# # print(significance_test)
# significance_test.to_csv('plots/norm/'+ prefix +'/'+ 'significance-test_' + ba +'.csv')