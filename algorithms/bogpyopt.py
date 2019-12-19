import numpy as np
import os
import json
import sys
from GPyOpt.methods import BayesianOptimization
from optimizer import optimizer

class boGPyOpt(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes,
                                                initial_samples=3, seed=1):
        super(boGPyOpt, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
        self.domain = [{'name': 'x', 'type': 'continuous', 'domain': (0,2)},
            {'name': 'y', 'type': 'continuous', 'domain': (0,2)},
            {'name': 'z', 'type': 'continuous', 'domain': (0,9)}]
        self.seed = seed
        self.initial_samples = initial_samples

    def convertToConfig(self, x):
        # x = bounds(x)
        type = self.types[int(round(x[0]))]
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getRuntime(self, x):
        type, size, num = self.convertToConfig(x[0])
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        return float(report["elapsed_time"])


    def runOptimizer(self):
        myBopt = BayesianOptimization(f=self.getRuntime, domain=self.domain)
        myBopt.run_optimization(max_iter=self.budget, verbosity=True)
        print(myBopt.x_opt, myBopt.fx_opt)
# print(myBopt.get_evaluations())
