import numpy as np
import os
import json
import sys
from optimizer import optimizer
from utils import *
import uuid

class randSearch(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes):
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

    def getRuntime(self, x1, x2, x3):
        type, size, num = [x1, x2, x3]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        if report["completed"]:
            runtime = float(report["elapsed_time"])
        else:
            runtime = 3600.0
        t = {'params': {'type': type,'size': size,'num': num}, 'runtime': runtime}
        updatePickle(t, filename=self.trialsFile)
        return runtime

    def runOptimizer(self):
        trails = list()
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
            val = self.getRuntime(parameters['type'], parameters['size'], parameters['num'])
            if val < value:
                value = val
                best_parameters = parameters
        print(value, best_parameters)
        trials = pickleRead(self.trialsFile)
        return trials
