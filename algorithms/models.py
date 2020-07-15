from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
import numpy as np
import os
import json
import sys
from skopt import gp_minimize, gbrt_minimize, forest_minimize, Optimizer
from skopt.space import Real, Integer, Categorical
from utils import *
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error

def getResult(filename, dir='hyperparam/'):
    data =dict()
    # print(results)
    if os.path.isfile(dir+filename):
        data = json.load(open(dir+filename, 'r'))
    return data

class models():
    def __init__(self, filename, app, system, datasize, budget, parent_dir, types, sizes,
                            number_of_nodes, optimizer='GP', acquisition_method='EI',
                                                initial_samples=3, seed=1, metric="Runtime"):
        self.app = app
        self.system = system
        self.datasize = datasize
        self.budget = budget
        self.parent_dir = parent_dir
        self.types = types
        self.sizes = sizes
        self.number_of_nodes = number_of_nodes
        self.trials = list()
        self.results = list()
        self.domain = [
                Categorical(self.types),
                Integer(0, len(self.sizes)-1),
                Integer(0, len(self.number_of_nodes[self.sizes[0]])-1)
        ]
        self.optimizer = optimizer
        self.seed = seed
        self.initial_samples = initial_samples
        self.acquisition_method = acquisition_method
        self.filename = filename
        self.metric = metric

    def convertToDom(self, x):
        # x = bounds(x)
        # print(x)
        type = x[0]
        size = self.sizes.index(x[1])
        num = self.number_of_nodes[x[1]].index(x[2])
        return type, size, num

    def convertToConfig(self, x):
        # x = bounds(x)
        type = x[0]
        # size = self.sizes[int(round(x[1]))]
        size = x[1]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    # def getRuntime(self, x):
    #     # print(x)
    #     # type, size, num = self.convertToConfig(x)
    #     type, size, num = x
    #     dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
    #     jsonName= dir + 'report.json'
    #     report = json.load(open(jsonName, 'r'))
    #     if report["completed"]:
    #         runtime = float(report["elapsed_time"])
    #     else:
    #         runtime = 3600.0
    #     return runtime

    def getObjective(self, x):
        type, size, num = self.convertToConfig(x)
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        if "cost" in self.metric:
            objective_value = getExecutionCost(jsonName, type, size, num)
        else:
            objective_value = getExecutionTime(jsonName, type, size, num)
        return objective_value


    def buildModel(self):
        if "cost" in self.metric:
            data = getResult(self.filename, dir='hyperparam_cost/')
        else:
            data = getResult(self.filename, dir='hyperparam/')
        
        

        X = list()
        Y = list()
        for type in self.types:
            for size in self.sizes:
                for num in self.number_of_nodes[size]:
                    # x = self.convertToDom([type, size, num])
                    x = type, size, num
                    # print(x)
                    X.append(list(x))
                    # print(x)
                    Y.append(self.getObjective(x))


        # print(X, Y)
        mse = list()
        ae = list()
        mae = list()
        for trials in data['experiments']:
            opt = Optimizer(self.domain, base_estimator=self.optimizer,
                n_random_starts=0, acq_optimizer="sampling",
                acq_func=self.acquisition_method,
                #acq_optimizer_kwargs={'n_points': 100}
                )
            conf = list()
            runtimes = list()
            for trial in trials:
                x = [ trial['params']['type'], trial['params']['size'], trial['params']['num'] ]
                # print(x)
                conf.append(self.convertToDom(x))
                runtimes.append(trial['value'])
                # opt.base_estimator_.fit(opt.space.transform([conf]), [trial['runtime']])
            opt.base_estimator_.fit(opt.space.transform(conf), runtimes)
            
            yTrue = list()
            yPred = list()
            for x,y in zip(X, Y):
                conf = self.convertToDom(x)
                pred = opt.base_estimator_.predict(opt.space.transform([conf]), [y])
                yTrue.append(y)
                yPred.append(pred[0][0])
            mse.append(mean_squared_error(yTrue, yPred))
            ae.append(mean_absolute_error(yTrue, yPred))
            mae.append(median_absolute_error(yTrue, yPred))
            # print(mse)
        rmse = np.sqrt(mse)
        return {'ae': ae, 'mae': mae, 'mse': mse, 'rmse': rmse}