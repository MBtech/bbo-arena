import numpy as np
import os
import json
import sys
from pyDOE import *
from optimizer import optimizer
from utils import *
import uuid

class lhsSearch(optimizer):
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

    def convertToConfig(self, x):
        type = self.types[int(round(x[0] * len(self.types)-1))]
        size = self.sizes[int(round(x[1] * len(self.sizes)-1))]
        index = int(round(x[2] * len(self.number_of_nodes[size])-1 ))
        num = self.number_of_nodes[size][index]
        return {'type':type, 'size':size, 'num' :num}

    def getObjectiveValue(self, x1, x2, x3):
        type, size, num = [x1, x2, x3]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        objective_value = self.objective_function(jsonName, type, size, num)
        t = {'params': {'type': type,'size': size,'num': num}, 'value': objective_value}
        updatePickle(t, filename=self.trialsFile)
        return objective_value

    def runOptimizer(self):
        trails = list()
        best_parameters = {}
        value = 100000
        lhd = lhs(3, samples=2*self.budget, criterion='center')
        # print(lhd)
        count = 0
        for i in range(0, 2*self.budget):
            parameters = self.convertToConfig(lhd[i])
            if parameters not in trails:
                count += 1
                val = self.getObjectiveValue(parameters['type'], parameters['size'], parameters['num'])
                trails.append(parameters)
            if val < value:
                value = val
                best_parameters = parameters

            if count == self.budget:
                break

        trials = pickleRead(self.trialsFile)
        print(value, best_parameters)

        return trials
