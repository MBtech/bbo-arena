import pickle
import os
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
