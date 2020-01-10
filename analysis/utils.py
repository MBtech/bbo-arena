import json

def getBest(app, system, datasize):
    parent_dir = '../scout/dataset/osr_multiple_nodes/'
    number_of_nodes = {
    'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
    'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
    '2xlarge': [4, 6, 8, 10, 12]
    }
    types = ['m4', 'c4', 'r4']
    sizes = ['large', 'xlarge', '2xlarge']

    runtimes = list()
    for t in types:
        for size in sizes:
            for num in number_of_nodes[size]:
                dir = parent_dir + str(num) + '_'+ t+'.'+size+ '_'+ app + "_" + system + "_" + datasize + "_1/"
                jsonName= dir + 'report.json'
                report = json.load(open(jsonName, 'r'))
                runtimes.append(float(report["elapsed_time"]))
    return min(runtimes)
    
def parseLogs(system, app, datasize, configJsonName = 'test_configs/all_runs.json'):
    config = json.load(open(configJsonName, 'r'))

    budget = config["budget"]
    optRuns = config["num_of_runs"]
    # optRuns = 10
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
                            best_time = singleExpData[i]['runtime']
                        if singleExpData[i+1]['runtime'] < best_time:
                            best_time = singleExpData[i]['runtime']
                        runtimes.append([algoName, count, best_time, i])
                else:
                    for run in singleExpData:
                        count +=1
                        if run['runtime'] < best_time:
                            best_time = run['runtime']
                        runtimes.append([algoName, count, best_time, i])
    return runtimes
