from hyperopt import fmin, tpe, hp, STATUS_OK, STATUS_FAIL
from functools import partial
import json
import sys
from optimizer import optimizer
import numpy as np

class tpeOptimizer(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes,
                                                initial_samples=3, seed=1):
        super(tpeOptimizer, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
        self.family = hp.choice('family', ['m4', 'c4', 'r4'])
        self.parameter_space = hp.choice('instance_class', [
            {
                'size': 'large',
                'family': self.family,
                'num_nodes': hp.randint('num_nodes1', 10),
            },
            {
                'size': 'xlarge',
                'family': self.family,
                'num_nodes': hp.randint('num_nodes2', 8),
            },
            {
                'size': '2xlarge',
                'family': self.family,
                'num_nodes': hp.randint('num_nodes3', 5)
            },
            ])
        self.seed = seed
        self.initial_samples = initial_samples

    def getRuntime(self, args):
        size = args['size']
        type = args['family']
        num = self.number_of_nodes[size][int(args['num_nodes'])]
        dir = self.parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ self.app + "_" +self.system + "_" + self.datasize + "_1/"
        jsonName= dir + 'report.json'
        report = json.load(open(jsonName, 'r'))
        runtime = float(report["elapsed_time"])
        if runtime < 0:
            # ret = {'loss': 3600, 'status': STATUS_OK}
            ret = {'loss': runtime, 'status': STATUS_FAIL}
        else:
            ret = {'loss': runtime, 'status': STATUS_OK}
        return ret


    def runOptimizer(self):
        algo = partial(tpe.suggest, n_startup_jobs=self.initial_samples)

        best = fmin(self.getRuntime,
            space=self.parameter_space,
            algo=algo,
            max_evals=self.budget,
            verbose=1,
            #points_to_evaluate=points_to_evaluate
            # rstate=np.random.RandomState(self.seed) # Setting this to a specific value making the algorithm determistic
            )

        print(best)
