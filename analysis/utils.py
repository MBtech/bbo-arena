import json
import os 
import sys

prices = {
    'm4.large': 0.1,
    'm4.xlarge': 0.20,
    'm4.2xlarge': 0.40,
    'c4.large': 0.10,
    'c4.xlarge': 0.199,
    'c4.2xlarge': 0.398,
    'r4.large': 0.133,
    'r4.xlarge': 0.266,
    'r4.2xlarge': 0.532,

    'm5.large': 0.096,
    'm5.xlarge': 0.192,
    'm5.2xlarge': 0.384,
    'm5.4xlarge': 0.768,

    'm5a.large': 0.086,
    'm5a.xlarge': 0.172,
    'm5a.2xlarge': 0.344,
    'm5a.4xlarge': 0.688,

    'c5.large': 0.085,
    'c5.xlarge': 0.17,
    'c5.2xlarge': 0.34,
    'c5.4xlarge': 0.68,

    'c5n.large': 0.108,
    'c5n.xlarge': 0.216,
    'c5n.2xlarge': 0.432,
    'c5n.4xlarge': 0.864,

    'r5.large': 0.126,
    'r5.xlarge': 0.252,
    'r5.2xlarge': 0.504,
    'r5.4xlarge': 1.008,
}

parent_dir = {'s': '../scout/dataset/osr_multiple_nodes/', 'l': '../experiments/dataset/'}
number_of_nodes = { 's':
    {   
    'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
    'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
    '2xlarge': [4, 6, 8, 10, 12]
    },
    'l': {
    'large': [16, 24, 32, 40, 48, 56, 64],
    'xlarge': [8, 12, 16, 20, 24, 28, 32],
    '2xlarge': [4, 6, 8, 10, 12, 14, 16], 
    '4xlarge': [2, 3, 4, 5, 6, 7, 8]
    }
}
types = {'s': ['m4', 'c4', 'r4'], 'l': ['m5', 'm5a', 'c5', 'c5n', 'r5'] }
sizes = {'s': ['large', 'xlarge', '2xlarge'], 'l': ['large', 'xlarge', '2xlarge', '4xlarge']}

# parent_dir = '../experiments/dataset/'
# number_of_nodes = {
#     'large': [16, 24, 32, 40, 48, 56, 64],
#     'xlarge': [8, 12, 16, 20, 24, 28, 32],
#     '2xlarge': [4, 6, 8, 10, 12, 14, 16], 
#     '4xlarge': [2, 3, 4, 5, 6, 7, 8]
# }
# types = ['m5', 'm5a', 'c5', 'c5n', 'r5']
# sizes = ['large', 'xlarge', '2xlarge', '4xlarge']

def getExecutionCost(jsonName, instType, instSize, num):
    price = prices[instType + '.' + instSize]
    report = json.load(open(jsonName, 'r'))
    runtime = float(report["elapsed_time"])
    cost = (price/3600.0)*runtime*num
    if not report["completed"]:
        cost = float('nan')
    return cost  


def getAll(app, system, datasize, metric="runtime", dataset='s'):
    runtimes = list()
    for t in types[dataset]:
        for size in sizes[dataset]:
            for num in number_of_nodes[dataset][size]:
                dir = parent_dir[dataset] + str(num) + '_'+ t+'.'+size+ '_'+ app + "_" + system + "_" + datasize + "_1/"
                if not os.path.isdir(dir):
                    return []

                jsonName= dir + 'report.json'
                if metric=="runtime":
                    report = json.load(open(jsonName, 'r'))
                    if report["completed"]:
                        runtime = float(report["elapsed_time"])
                    else:
                        runtime = float('nan')
                else:
                    runtime = getExecutionCost(jsonName, t, size, num)
                # if runtime > 0:
                runtimes.append([runtime, num, t, size])
    return runtimes
    
def getBest(app, system, datasize, dataset='s'):
    runtimes = list()
    for t in types[dataset]:
        for size in sizes[dataset]:
            for num in number_of_nodes[dataset][size]:
                dir = parent_dir[dataset] + str(num) + '_'+ t+'.'+size+ '_'+ app + "_" + system + "_" + datasize + "_1/"
                if not os.path.isdir(dir):
                    return []
                
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
        if "bo1" in algo:
            for estimator in config["bo_estimators"]:
                for acq_method in config["bo_acq"][estimator]:
                    for i in range(0, optRuns):
                        algoName = algo
                        algoName += '_' + estimator + '_' + acq_method
                        new_filename = filename + '_' + estimator + '_' + acq_method
                        try:
                            data = json.load(open(logDir + new_filename))
                        except:
                            print(logDir + new_filename)
                            sys.exit()
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
        if "bo1" in algo:
            for estimator in config["bo_estimators"]:
                for acq_method in config["bo_acq"][estimator]:
                    for i in range(0, optRuns):
                        algoName = algo
                        algoName += '_' + estimator + '_' + acq_method
                        new_filename = filename + '_' + estimator + '_' + acq_method
                        if not os.path.isfile(logDir + new_filename):
                            return []
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
                if not os.path.isfile(logDir + filename):
                    return []
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