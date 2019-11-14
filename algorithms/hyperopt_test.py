from hyperopt import fmin, tpe, hp, STATUS_OK, STATUS_FAIL
from functools import partial
import json
import sys

def objective(args):
    print(args)
    size = args['size']
    type = args['family']
    num = configs[size][int(args['num_nodes'])]
    dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
    jsonName= dir + 'report.json'
    report = json.load(open(jsonName, 'r'))
    runtime = float(report["elapsed_time"])
    if runtime < 0:
        # ret = {'loss': 3600, 'status': STATUS_OK}
        ret = {'loss': runtime, 'status': STATUS_FAIL}
    else:
        ret = {'loss': runtime, 'status': STATUS_OK}
    return ret


configs = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark1.5
app =sys.argv[1]
system = sys.argv[2]
datasize = 'huge'

family = hp.choice('family', ['m4', 'c4', 'r4'])
space = hp.choice('instance_class', [
    {
        'size': 'large',
        'family': family,
        'num_nodes': hp.randint('num_nodes1', 10),
    },
    {
        'size': 'xlarge',
        'family': family,
        'num_nodes': hp.randint('num_nodes2', 8),
    },
    {
        'size': '2xlarge',
        'family': family,
        'num_nodes': hp.randint('num_nodes3', 5)
    },
    ])

algo = partial(tpe.suggest, n_startup_jobs=3)

best = fmin(objective,
    space=space,
    algo=algo,
    max_evals=15,
    verbose=1,
    #points_to_evaluate=points_to_evaluate
    )

print(best)
