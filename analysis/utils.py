import json

def parseLogs(system, app, datasize, configJsonName = 'test_configs/all_runs.json'):
    config = json.load(open(configJsonName, 'r'))

    budget = config["budget"]
    # optRuns = config["num_of_runs"]
    optRuns = 10
    logDir = "../algorithms/logs/"

    runtimes = list()
    algoName = ""
    for algo in config["bbo_algos"]:
        algoName = algo
        filename = system + '_' + app + '_' + datasize + '_' + algo
        # Since there are multiple version of BO we have separated it
        if algo == "bo":
            for estimator in config["bo_estimators"]:
                for acq_method in config["bo_acq"][estimator]:
                    for i in range(0, optRuns):
                        algoName = algo
                        algoName += '_' + estimator + '_' + acq_method
                        new_filename = filename + '_' + estimator + '_' + acq_method

                        data = json.load(open(logDir + new_filename))
                        runs = len(data['experiments'][i])
                        singleExpData = data['experiments'][i]
                        count = 0
                        best_time = float('Inf')
                        for run in singleExpData:
                            count +=1
                            if run['runtime'] < best_time:
                                best_time = run['runtime']
                            runtimes.append([algoName, count, best_time, i])

        else:
            for i in range(0, optRuns):
                filename = system + '_' + app + '_' + datasize + '_' + algo

                data = json.load(open(logDir + filename))
                runs = len(data['experiments'][i])
                singleExpData = data['experiments'][i]
                count = 0
                best_time = float('Inf')
                if algo == "random2x":
                    # random2x need a step of 2 because it'd have 2 the budget
                    for i in range(0, len(singleExpData), 2):
                        count +=1
                        if singleExpData[i]['runtime'] < best_time:
                            best_time = run['runtime']
                        if singleExpData[i+1]['runtime'] < best_time:
                            best_time = run['runtime']
                        runtimes.append([algoName, count, best_time, i])
                else:
                    for run in singleExpData:
                        count +=1
                        if run['runtime'] < best_time:
                            best_time = run['runtime']
                        runtimes.append([algoName, count, best_time, i])
    return runtimes
