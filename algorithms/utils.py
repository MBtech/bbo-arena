import pickle
import os
import json
import time

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

number_of_nodes = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'


# parent_dir = '../experiments/dataset/'
# number_of_nodes = {
#     'large': [16, 24, 32, 40, 48, 56, 64],
#     'xlarge': [8, 12, 16, 20, 24, 28, 32],
#     '2xlarge': [4, 6, 8, 10, 12, 14, 16], 
#     '4xlarge': [2, 3, 4, 5, 6, 7, 8]
# }
# types = ['m5', 'm5a', 'c5', 'c5n', 'r5']
# sizes = ['large', 'xlarge', '2xlarge', '4xlarge']

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

def getExecutionCost(jsonName, instType, instSize, num):
    price = prices[instType + '.' + instSize]
    report = json.load(open(jsonName, 'r'))
    runtime = float(report["elapsed_time"])
    cost = (price/3600.0)*runtime*num
    if not report["completed"]:
        cost = 100.0
    return cost  

def getExecutionTime(jsonName, instType, instSize, num):
    report = json.load(open(jsonName, 'r'))
    if report["completed"]:
        runtime = float(report["elapsed_time"])
    else:
        runtime = 3600.0
    return runtime

def pickleWrite(filename, data):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def pickleRead(filename, default=[]):
    if os.path.isfile(filename):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)
        os.remove(filename)
        return data
    else:
        return default

def updatePickle(trial, filename='trials.pickle', default={'trials':[]}):
    trials = pickleRead(filename, default={'trials':[]})
    trials['trials'].append(trial)
    pickleWrite(filename, trials)
