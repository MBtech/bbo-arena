import numpy as np
import os
import json
import sys

def convertToConfig(x):
    type = types[int(round(x[0]))]
    size = sizes[int(round(x[1]))]
    index = int(round(x[2])) % len(configs[size])
    num = configs[size][index]
    return type, size, num

def get_runtime(x1, x2, x3):
    type, size, num = [x1, x2, x3]
    dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
    jsonName= dir + 'report.json'
    report = json.load(open(jsonName, 'r'))
    return float(report["elapsed_time"])

configs = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark
app =sys.argv[1]
system = sys.argv[2]
datasize = 'huge'
budget = 15
trails = list()
best_parameters = {}
value = 100000
for i in range(0, budget):
    parameters = {}
    parameters['type'] = np.random.choice(types)
    parameters['size'] = np.random.choice(sizes)
    parameters['num'] = np.random.choice(configs[parameters['size']])
    val = get_runtime(parameters['type'], parameters['size'], parameters['num'])
    if val < value:
        value = val
        best_parameters = parameters

print(value, best_parameters)
