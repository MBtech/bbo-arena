import sys
from lhssearch import *
from randsearch import *
from smac import *
from tpe import *
from bogpyopt import *
from boskopt import boSkOpt
from hillclimbing import hcOpt
from simulatedannealing import saOpt
import json
import os
import time
from joblib import Parallel, delayed


def getResults(search, filename, config, dir='logs/'):
    log = config['log']
    for i in range(0, config["num_of_runs"]):
        results = search.runOptimizer()
        data =dict()
        # print(results)
        if os.path.isfile(dir+filename):
            data = json.load(open(dir+filename, 'r'))
        else:
            data['experiments'] = []
        # print(results)
        data['experiments'].append(results['trials'])

        if log:
            json.dump(data, open(dir+filename, 'w'), indent=4)

def callBO(system, app, datasize, algo, budget, parent_dir, types, sizes, number_of_nodes, config, estimator, acq_method, filename):
    new_filename = filename + '_' + estimator + '_' + acq_method
    print(new_filename)
    search = boSkOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, optimizer=estimator, 
                        initial_samples=config["initial_samples"], acquisition_method=acq_method)
    getResults(search, new_filename, config)


def callOptimizer(system, app, datasize, algo, budget, parent_dir, types, sizes, number_of_nodes, config):
    filename = system + '_' + app + '_' + datasize + '_' + algo
    if algo == "lhs":
        search = lhsSearch(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
    elif algo == "random":
        search = randSearch(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
    elif algo == "random2x":
        search = randSearch(app, system, datasize, 2*budget, parent_dir, types, sizes, number_of_nodes)
    elif algo == "smac":
        search = smac(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
    elif algo == "tpe":
        search = tpeOptimizer(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, initial_samples=config["initial_samples"])

    elif "bo" in algo:
        Parallel(n_jobs=nJobs)(delayed(callBO)(system, app, datasize, algo, budget, parent_dir, types, sizes, number_of_nodes, config, estimator, acq_method, filename )
                    for estimator in config["bo_estimators"] for acq_method in config["bo_acq"][estimator])


    elif "hc" in algo:
        search = hcOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, initial_samples=config["initial_samples"])
    elif "sa" in algo:
        search = saOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, initial_samples=config["initial_samples"])

    else:
        print("Algorithm not found")


    if "bo" not in algo:
        getResults(search, filename, config)


number_of_nodes = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark
config = json.load(open(sys.argv[1], 'r'))

budget = config["budget"]
nJobs = 4

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            for algo in config["bbo_algos"]:
                callOptimizer(system, app, datasize, algo, budget, parent_dir, types, sizes, number_of_nodes, config) 
                                                




# search = boGPyOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
