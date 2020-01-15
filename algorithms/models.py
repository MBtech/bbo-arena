from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
import numpy as np
import os
import json
import sys
from skopt import gp_minimize, gbrt_minimize, forest_minimize, Optimizer
from skopt.space import Real, Integer, Categorical
from utils import *
from sklearn.metrics import mean_squared_error

def getResult(filename, dir='logs/'):
    data =dict()
    # print(results)
    if os.path.isfile(dir+filename):
        data = json.load(open(dir+filename, 'r'))
    return data

class models():
    def __init__(self, filename, app, system, datasize, budget, parent_dir, types, sizes,
                            number_of_nodes, optimizer='GP', acquisition_method='EI',
                                                initial_samples=3, seed=1):
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
        size = self.sizes[int(round(x[1]))]
        index = int(round(x[2])) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]
        return type, size, num

    def getRuntime(self, x):
        # print(x)
        # type, size, num = self.convertToConfig(x)
        type, size, num = x
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        if report["completed"]:
            runtime = float(report["elapsed_time"])
        else:
            runtime = 3600.0
        return runtime


    def buildModel(self):

        data = getResult(self.filename)

        X = list()
        Y = list()
        for type in self.types:
            for size in self.sizes:
                for num in self.number_of_nodes[size]:
                    # x = self.convertToDom([type, size, num])
                    x = type, size, num
                    # print(x)
                    X.append(list(x))
                    Y.append(self.getRuntime(x))


        # print(X, Y)
        mse = list()
        for trials in data['experiments']:
            opt = Optimizer(self.domain, base_estimator=self.optimizer,
                n_random_starts=self.initial_samples, acq_optimizer="sampling",
                acq_func=self.acquisition_method,
                #acq_optimizer_kwargs={'n_points': 100}
                )
            for trial in trials:
                x = [ trial['params']['type'], trial['params']['size'], trial['params']['num'] ]
                conf = self.convertToDom(x)
                opt.base_estimator_.fit(opt.space.transform([conf]), [trial['runtime']])
            
            yTrue = list()
            yPred = list()
            for x,y in zip(X, Y):
                conf = self.convertToDom(x)
                pred = opt.base_estimator_.predict(opt.space.transform([conf]), [y])
                yTrue.append(y)
                yPred.append(pred[0][0])
            mse.append(mean_squared_error(yTrue, yPred))
            # print(mse)
        rmse = np.sqrt(mse)
        return {'mse': mse, 'rmse': rmse}