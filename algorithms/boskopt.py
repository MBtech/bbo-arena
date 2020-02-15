import numpy as np
import os
import json
import sys
from skopt import gp_minimize, gbrt_minimize, forest_minimize, Optimizer
from optimizer import optimizer
from skopt.space import Real, Integer, Categorical
from utils import *
import uuid

class boSkOpt(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes,
                            number_of_nodes, objective_function, optimizer='GP', acquisition_method='EI',
                                                initial_samples=3, seed=1):
        super(boSkOpt, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, objective_function)
        self.domain = [
                Categorical(self.types),
                Integer(0, len(self.sizes)-1),
                Integer(0, len(self.number_of_nodes[self.sizes[0]])-1)
        ]
        self.optimizer = optimizer
        self.seed = seed
        self.initial_samples = initial_samples
        self.acquisition_method = acquisition_method
        self.uuid = uuid.uuid4().hex
        self.trialsFile = 'trials-'+self.uuid+'.pickle'
        

    def convertToConfig(self, x):
        # x = bounds(x)
        type = x[0]
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getObjectiveValue(self, x):
        # print(x)
        type, size, num = self.convertToConfig(x)
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        objective_value = self.objective_function(jsonName, type, size, num)
        t = {'params': {'type': type,'size': size,'num': num}, 'value': objective_value}
        updatePickle(t, filename=self.trialsFile)
        return objective_value


    def runOptimizer(self):
        # if self.optimizer=='gp':
        #     res = gp_minimize(self.getRuntime, self.domain, n_calls=self.budget,
        #                 n_random_starts=self.initial_samples)
        # elif self.optimizer=='gbrt':
        #     res = gbrt_minimize(self.getRuntime, self.domain, n_calls=self.budget,
        #             n_random_starts=self.initial_samples)
        # elif self.optimizer=='forest':
        #     res = forest_minimize(self.getRuntime, self.domain, n_calls=self.budget,
        #             n_random_starts=self.initial_samples)
        opt = Optimizer(self.domain, base_estimator=self.optimizer,
                n_random_starts=self.initial_samples, acq_optimizer="sampling",
                acq_func=self.acquisition_method
                #acq_optimizer_kwargs={'n_points': 100}
                )
        count = 0
        trails = list()
        results = list()
        min_x = list()
        min_val = 10000
        while count < self.budget:
            next_x = opt.ask()
            if next_x not in trails:
                f_val = self.getObjectiveValue(next_x)
                count +=1
                if f_val < min_val:
                    min_val = f_val
                    min_x = next_x
                trails.append(next_x)
                results.append(f_val)
            else:
                f_val = results[trails.index(next_x)]
            opt.tell(next_x, f_val)

        best_parameters = dict()
        best_parameters['type'], best_parameters['size'], best_parameters['num'] = self.convertToConfig(min_x)
        print(min_val, best_parameters)
        trials = pickleRead(self.trialsFile)
        return trials
