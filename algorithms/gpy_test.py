import numpy as np
import os
import json
import sys
from GPyOpt.methods import BayesianOptimization

# def bounds(x):
#     x[0] = min(max(int(round(x[0])), 0), len(types)-1)
#     x[1] = min(max(int(round(x[1])), 0), len(sizes)-1)
#     x[2] = min(max(int(round(x[2])), 0), len(configs[sizes[int(x[1])]])-1)
#     return x

def convertToConfig(x):
    # x = bounds(x)
    type = types[int(round(x[0]))]
    size = sizes[int(round(x[1]))]
    index = int(round(x[2])) % len(configs[size])
    num = configs[size][index]
    return type, size, num

def get_runtime(x):
    type, size, num = convertToConfig(x[0])
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

# python plot_all_runtimes.py pagerank spark1.5
app =sys.argv[1]
system = sys.argv[2]
datasize = 'huge'

domain = [{'name': 'x', 'type': 'continuous', 'domain': (0,2)},
        {'name': 'y', 'type': 'continuous', 'domain': (0,2)},
        {'name': 'z', 'type': 'continuous', 'domain': (0,9)}]
myBopt = BayesianOptimization(f=get_runtime, domain=domain)
myBopt.run_optimization(max_iter=15, verbosity=True)
print(myBopt.x_opt, myBopt.fx_opt)
# print(myBopt.get_evaluations())
