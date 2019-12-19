import numpy as np
import os
import json
import sys
from skopt import gp_minimize
from skopt import gbrt_minimize
from skopt import forest_minimize
from optimizer import optimizer
from skopt.space import Real, Integer, Categorical

class boSkOpt(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, optimizer='gp',
                                                initial_samples=3, seed=1):
        super(boSkOpt, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
        self.domain = [
                Categorical(self.types),
                Integer(0, len(self.sizes)-1),
                Integer(0, len(self.number_of_nodes[self.sizes[0]])-1)
        ]
        self.optimizer = optimizer
        self.seed = seed
        self.initial_samples = initial_samples

    def convertToConfig(self, x):
        # x = bounds(x)
        type = x[0]
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getRuntime(self, x):
        print(x)
        type, size, num = self.convertToConfig(x)
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        return float(report["elapsed_time"])


    def runOptimizer(self):
        if self.optimizer=='gp':
            res = gp_minimize(self.getRuntime, self.domain, n_calls=self.budget,
                        n_random_starts=self.initial_samples)
        elif self.optimizer=='gbrt':
            res = gbrt_minimize(self.getRuntime, self.domain, n_calls=self.budget,
                    n_random_starts=self.initial_samples)
        elif self.optimizer=='forest':
            res = forest_minimize(self.getRuntime, self.domain, n_calls=self.budget,
                    n_random_starts=self.initial_samples)
                    
        print(res['fun'], res['x'])
# print(myBopt.get_evaluations())
