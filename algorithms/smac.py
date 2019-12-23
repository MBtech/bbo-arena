import numpy as np
import os
import json
import sys
# from smac.facade.func_facade import fmin_smac
import pysmac
from optimizer import optimizer

class smac(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes,
        parameter_space= {'x1':('categorical', ['m4', 'c4', 'r4'], 'm4'),
                        'x2':('integer', [0, 2], 1),
                        'x3':('integer', [0, 9], 1)
                        }):
        self.parameter_space = parameter_space
        super(smac, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)


    def convertToConfig(self, x):
        type = x[0]
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getRuntime(self, x1, x2, x3):
        x = [x1, x2, x3]
        type, size, num = self.convertToConfig(x)
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" + self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        return float(report["elapsed_time"])

    def runOptimizer(self):
        # x, cost, _ = fmin_smac(func=get_runtime,
        #                        x0=[1, 1, 1],
        #                        bounds=[(1, 3), (1, 3), (1, 10)],
        #                        maxfun=10,
        #                        rng=3)

        opt = pysmac.SMAC_optimizer()
        value, parameters = opt.minimize(
                            self.getRuntime,
                            self.budget,
                            self.parameter_space)
        best_parameters=dict()
        best_parameters['type'], best_parameters['size'],  best_parameters['num'] = \
                        self.convertToConfig([parameters['x1'],parameters['x2'], parameters['x3']])
        print(value, best_parameters)
        return {'value': value, 'params': best_parameters}
