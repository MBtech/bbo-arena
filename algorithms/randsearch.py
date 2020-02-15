import numpy as np
import os
import json
import sys
from optimizer import optimizer
from utils import *
import uuid

class randSearch(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, objective_function):
        self.app = app
        self.system = system
        self.datasize = datasize
        self.budget = budget
        self.parent_dir = parent_dir
        self.types = types
        self.sizes = sizes
        self.number_of_nodes = number_of_nodes
        self.uuid = uuid.uuid4().hex
        self.trialsFile = 'trials-'+self.uuid+'.pickle'
        self.objective_function = objective_function

    def getObjectiveValue(self, x1, x2, x3):
        type, size, num = [x1, x2, x3]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        objective_value = self.objective_function(jsonName, type, size, num)
        t = {'params': {'type': type,'size': size,'num': num}, 'value': objective_value}
        updatePickle(t, filename=self.trialsFile)
        return objective_value

    def runOptimizer(self):
        all_trails = list()
        best_parameters = {}
        count = 0
        value = 100000
        while count < self.budget:
            parameters = {}
            parameters['type'] = np.random.choice(self.types)
            parameters['size'] = np.random.choice(self.sizes)
            parameters['num'] = int(np.random.choice(self.number_of_nodes[parameters['size']]))
            if parameters in all_trails:
                continue
            all_trails.append(parameters)
            count += 1
            val = self.getObjectiveValue(parameters['type'], parameters['size'], parameters['num'])
            if val < value:
                value = val
                best_parameters = parameters
        print(value, best_parameters)
        trials = pickleRead(self.trialsFile)
        return trials
