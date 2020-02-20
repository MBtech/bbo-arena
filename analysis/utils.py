import json

prices = {
    'm4.large': 0.1,
    'm4.xlarge': 0.20,
    'm4.2xlarge': 0.40,
    'c4.large': 0.10,
    'c4.xlarge': 0.199,
    'c4.2xlarge': 0.398,
    'r4.large': 0.03,
    'r4.xlarge': 0.05,
    'r4.2xlarge': 0.1,
}

def getExecutionCost(jsonName, instType, instSize, num):
    price = prices[instType + '.' + instSize]
    report = json.load(open(jsonName, 'r'))
    runtime = float(report["elapsed_time"])
    cost = (price/3600.0)*runtime*num
    if not report["completed"]:
        cost = -1
    return cost  


def getAll(app, system, datasize, metric="runtime"):
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
                if metric=="runtime":
                    report = json.load(open(jsonName, 'r'))
                    if report["completed"]:
                        runtime = float(report["elapsed_time"])
                    else:
                        runtime = 3600.0
                else:
                    runtime = getExecutionCost(jsonName, t, size, num)
                if runtime > 0:
                    runtimes.append([runtime, num, t, size])
    return runtimes
    
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
                if report["completed"]:
                    runtime = float(report["elapsed_time"])
                else:
                    runtime = 3600.0
                runtimes.append(runtime)
                # print(str(num) + '_'+ t+'.'+size, runtime)
    return min(runtimes)
    
def parseLogs(system, app, datasize, configJsonName = 'test_configs/all_runs.json', logDir='../algorithms/logs/', value_key='value'):
    config = json.load(open(configJsonName, 'r'))

    budget = config["budget"]
    optRuns = config["num_of_runs"]
    # optRuns = 10

    runtimes = list()
    algoName = ""
    for algo in config["bbo_algos"]:
        algoName = algo
        filename = system + '_' + app + '_' + datasize + '_' + algo
        # Since there are multiple version of BO we have separated it
        if "bo" in algo:
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
                            if run[value_key] < best_time:
                                best_time = run[value_key]
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
                        if singleExpData[i][value_key] < best_time:
                            best_time = singleExpData[i][value_key]
                        if singleExpData[i+1][value_key] < best_time:
                            best_time = singleExpData[i][value_key]
                        runtimes.append([algoName, count, best_time, i])
                else:
                    for run in singleExpData:
                        count +=1
                        if run[value_key] < best_time:
                            best_time = run[value_key]
                        runtimes.append([algoName, count, best_time, i])
    return runtimes

def parseLogsAll(system, app, datasize, configJsonName = 'test_configs/all_runs.json', logDir='../algorithms/logs/', value_key='value'):
    config = json.load(open(configJsonName, 'r'))

    budget = config["budget"]
    optRuns = config["num_of_runs"]
    # optRuns = 10

    runtimes = list()
    algoName = ""
    for algo in config["bbo_algos"]:
        algoName = algo
        filename = system + '_' + app + '_' + datasize + '_' + algo
        # Since there are multiple version of BO we have separated it
        if "bo" in algo:
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
                            best_time = run[value_key]
                            instType = run["params"]["type"]
                            instSize = run["params"]["size"]
                            instNum = run["params"]["num"]
                            runtimes.append([algoName, count, best_time, i, instType, instSize, instNum])

        else:
            for i in range(0, optRuns):
                filename = system + '_' + app + '_' + datasize + '_' + algo

                data = json.load(open(logDir + filename))
                runs = len(data['experiments'][i])
                singleExpData = data['experiments'][i]
                count = 0
                best_time = float('Inf')
                if algo == "random2x":
                    continue
                    # # random2x need a step of 2 because it'd have 2 the budget
                    # for i in range(0, len(singleExpData), 2):
                    #     count +=1
                    #     best_time = singleExpData[i]['runtime']
                    #     runtimes.append([algoName, count, best_time, i, instType, instSize, instNum])
                    #     best_time = singleExpData[i]['runtime']
                    #     runtimes.append([algoName, count, best_time, i, instType, instSize, instNum])
                        
                else:
                    for run in singleExpData:
                        count +=1
                        best_time = run[value_key]
                        instType = run["params"]["type"]
                        instSize = run["params"]["size"]
                        instNum = run["params"]["num"]
                        runtimes.append([algoName, count, best_time, i, instType, instSize, instNum])
    return runtimes