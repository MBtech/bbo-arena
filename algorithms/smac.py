import numpy as np
import os
import json
import sys
# from smac.facade.func_facade import fmin_smac
import pysmac
from optimizer import optimizer
from utils import *

class smac(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes):
        parameter_space= {'x1':('categorical', types, np.random.choice(types)),
                        'x2':('integer', [0, len(sizes)-1], int(np.random.choice(range(0, len(sizes))))),
                        'x3':('integer', [0, 9], int(np.random.choice(range(0, 10))))
                        }
        self.forbidden_confgs = [
                        "{x2 == 1 && x3 > 7 }",
                        "{x3 == 2 && x3 > 4 }"
                        ]
        self.parameter_space = parameter_space
        self.count = 0
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
        # print(type, size, num)
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" + self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        t = {'params': {'type': type,'size': size,'num': num}, 'runtime': float(report["elapsed_time"])}
        updatePickle(t)
        return float(report["elapsed_time"])

    def runOptimizer(self):
        # x, cost, _ = fmin_smac(func=get_runtime,
        #                        x0=[1, 1, 1],
        #                        bounds=[(1, 3), (1, 3), (1, 10)],
        #                        maxfun=10,
        #                        rng=3)
        if not os.path.isdir(os.getcwd()+"/temp"):
            os.mkdir(os.getcwd()+"/temp")
        opt = pysmac.SMAC_optimizer(working_directory =os.getcwd()+"/temp")
        value, parameters = opt.minimize(
                            self.getRuntime,
                            self.budget,
                            self.parameter_space,
                            forbidden_clauses=self.forbidden_confgs)
        opt.__del__()
        best_parameters=dict()
        best_parameters['type'], best_parameters['size'],  best_parameters['num'] = \
                        self.convertToConfig([parameters['x1'],parameters['x2'], parameters['x3']])
        trials = pickleRead('trials.pickle')
        print(value, best_parameters)
        # return {'value': value, 'params': best_parameters}
        print(trials)
        return trials
