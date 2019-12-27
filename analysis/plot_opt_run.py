import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
sns.set(style="white grid")

config = json.load(open('../algorithms/test_configs/all_runs.json', 'r'))

budget = config["budget"]
# optRuns = config["num_of_runs"]
optRuns = 1
logDir = "../algorithms/logs/"
df = pd.DataFrame()

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            runtimes = list()
            algoName = ""
            for algo in config["bbo_algos"]:
                algoName = algo
                filename = system + '_' + app + '_' + datasize + '_' + algo

                if algo == "bo":
                    for estimator in config["bo_estimators"]:
                        for acq_method in config["bo_acq"][estimator]:
                            for i in range(0, optRuns):
                                algoName = algo
                                algoName += '_' + estimator + '_' + acq_method
                                new_filename = filename + '_' + estimator + '_' + acq_method

                                data = json.load(open(logDir + new_filename))
                                runs = len(data['experiments'][0])
                                singleExpData = data['experiments'][0]
                                count = 0
                                best_time = float('Inf')
                                for run in singleExpData:
                                    count +=1
                                    if run['runtime'] < best_time:
                                        best_time = run['runtime']
                                    runtimes.append([algoName, count, best_time])

                else:
                    for i in range(0, optRuns):
                        filename = system + '_' + app + '_' + datasize + '_' + algo

                        data = json.load(open(logDir + filename))
                        runs = len(data['experiments'][0])
                        singleExpData = data['experiments'][0]
                        count = 0
                        best_time = float('Inf')
                        if algo == "random2x":
                            for i in range(0, len(singleExpData), 2):
                                count +=1
                                if singleExpData[i]['runtime'] < best_time:
                                    best_time = run['runtime']
                                if singleExpData[i+1]['runtime'] < best_time:
                                    best_time = run['runtime']
                                runtimes.append([algoName, count, best_time])
                        else:
                            for run in singleExpData:
                                count +=1
                                if run['runtime'] < best_time:
                                    best_time = run['runtime']
                                runtimes.append([algoName, count, best_time])

            df = pd.DataFrame(runtimes, columns = ['Algo', 'Budget', 'Runtime'])
            # print(df)
            sns.lineplot(x='Budget', y='Runtime', hue="Algo", data=df)
            plt.legend(loc='upper right', ncol=3)
            plt.show()
