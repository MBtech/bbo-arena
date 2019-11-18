import numpy as np
import os
import json
import sys
# from smac.facade.func_facade import fmin_smac
import pysmac

def convertToConfig(x):
    type = types[int(round(x[0]))]
    size = sizes[int(round(x[1]))]
    index = int(round(x[2])) % len(configs[size])
    num = configs[size][index]
    return type, size, num

def get_runtime(x1, x2, x3):
    print(x1, x2, x3)
    x = [x1, x2, x3]
    type, size, num = convertToConfig(x)
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

# x, cost, _ = fmin_smac(func=get_runtime,
#                        x0=[1, 1, 1],
#                        bounds=[(1, 3), (1, 3), (1, 10)],
#                        maxfun=10,
#                        rng=3)

opt = pysmac.SMAC_optimizer()
parameters= {'x1':('integer', [0, 2], 1),
            'x2':('integer', [0, 2], 1),
            'x3':('integer', [0, 9], 1)
            }
value, parameters = opt.minimize(
                    get_runtime,
                    10,
                    parameters)
print(value, parameters)
