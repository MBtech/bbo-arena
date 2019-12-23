import numpy as np
import os
import json
import sys
from optimizer import optimizer

class randSearch(optimizer):
    # def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes):
    #     self.app = app
    #     self.system = system
    #     self.datasize = datasize
    #     self.budget = budget
    #     self.parent_dir = parent_dir
    #     self.types = types
    #     self.sizes = sizes
    #     self.number_of_nodes = number_of_nodes

    def getRuntime(self, x1, x2, x3):
        type, size, num = [x1, x2, x3]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        return float(report["elapsed_time"])

    def runOptimizer(self):
        trails = list()
        best_parameters = {}
        value = 100000
        for i in range(0, self.budget):
            parameters = {}
            parameters['type'] = np.random.choice(self.types)
            parameters['size'] = np.random.choice(self.sizes)
            parameters['num'] = np.random.choice(self.number_of_nodes[parameters['size']])
            val = self.getRuntime(parameters['type'], parameters['size'], parameters['num'])
            if val < value:
                value = val
                best_parameters = parameters

        print(value, best_parameters)
        return {'value': value, 'params': best_parameters}
