from hyperopt import fmin, tpe, hp, STATUS_OK, STATUS_FAIL, space_eval
from functools import partial
import json
import sys
from optimizer import optimizer
import numpy as np
import re
from utils import *
import uuid

class tpeOptimizer(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, objective_function, points_to_evaluate=[],
                                                initial_samples=3, seed=1, gamma=0.25):
        super(tpeOptimizer, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, objective_function, points_to_evaluate)
        self.family = hp.choice('type', self.types)
        # self.classes = [
        #     {
        #         'size': 'large',
        #         'type': self.family,
        #         'num': hp.randint('num_nodes1', 10),
        #     },
        #     {
        #         'size': 'xlarge',
        #         'type': self.family,
        #         'num': hp.randint('num_nodes2', 8),
        #     },
        #     {
        #         'size': '2xlarge',
        #         'type': self.family,
        #         'num': hp.randint('num_nodes3', 5)
        #     },
        #     ]
        self.parameter_space = {
            'type': hp.choice('type', self.types),
            'size': hp.choice('size', self.sizes),
            'num': hp.randint('num', 10)
        }
        # self.parameter_space = hp.choice('instance_class', self.classes)
        self.seed = seed
        self.initial_samples = initial_samples
        self.uuid = uuid.uuid4().hex
        self.trialsFile = 'trials-'+self.uuid+'.pickle'
        self.gamma = gamma

    def getObjectiveValue(self, args):
        # print(args)
        size = args['size']
        type = args['type']

        index = int(args['num']) % len(self.number_of_nodes[size])
        num = self.number_of_nodes[size][index]

        # print(type, size, str(num))
        # num = self.number_of_nodes[size][int(args['num'])]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        objective_value = self.objective_function(jsonName, type, size, num)
        t = {'params': {'type': type,'size': size,'num': num}, 'value': objective_value}
        updatePickle(t, filename=self.trialsFile)
        ret = {'loss': objective_value, 'status': STATUS_OK}
        # if objective_value == 3600.0:
        #     # ret = {'loss': 3600, 'status': STATUS_OK}
        #     ret = {'loss': objective_value, 'status': STATUS_FAIL}
        # else:
        #     ret = {'loss': objective_value, 'status': STATUS_OK}
        return ret

    def convert_points(self, points_to_evaluate):
        pte = list()
        for point in points_to_evaluate:
            # print(point)
            p = dict()
            p["num"] = self.number_of_nodes[point["size"]].index(point["num"])
            p["type"] = self.types.index(point["type"])
            p["size"] = self.sizes.index(point["size"])
            pte.append(p)
        return pte

    def runOptimizer(self):
        algo = partial(tpe.suggest, n_startup_jobs=self.initial_samples, gamma=self.gamma)

        pte = self.convert_points(self.points_to_evaluate)

        best_parameters = fmin(self.getObjectiveValue,
            space=self.parameter_space,
            algo=algo,
            max_evals=self.budget-len(pte),
            verbose=False,
            show_progressbar=False,
            points_to_evaluate=pte,
            trials=None,
            #points_to_evaluate=points_to_evaluate
            # rstate=np.random.RandomState(self.seed) # Setting this to a specific value making the algorithm determistic
            )

        param = space_eval(self.parameter_space, best_parameters)
        value = self.getObjectiveValue(param)
        trials = pickleRead(self.trialsFile)
        print(value['loss'], param)
        return trials
