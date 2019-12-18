import numpy as np
import os
import json
import sys
# from smac.facade.func_facade import fmin_smac
import pysmac
from optimizer import optimizer

class smac(optimizer):
    def convertToConfig(self, x):
        type = self.types[int(round(x[0]))]
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getRuntime(self, x1, x2, x3):
        print(x1, x2, x3)
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
        parameters= {'x1':('integer', [0, 2], 1),
                    'x2':('integer', [0, 2], 1),
                    'x3':('integer', [0, 9], 1)
                    }
        value, parameters = opt.minimize(
                            self.getRuntime,
                            10,
                            parameters)
        print(value, parameters)
