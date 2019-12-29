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

def getResult(search, filename, dir='logs/', log=True):
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

number_of_nodes = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark
config = json.load(open('test_configs/single_algo.json', 'r'))

budget = config["budget"]

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            for algo in config["bbo_algos"]:
                for i in range(0, config["num_of_runs"]):
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
                        search = tpeOptimizer(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)

                    elif algo == "bo":
                        for estimator in config["bo_estimators"]:
                            for acq_method in config["bo_acq"][estimator]:
                                new_filename = filename + '_' + estimator + '_' + acq_method
                                search = boSkOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, optimizer=estimator, initial_samples=6, acquisition_method=acq_method)
                                getResult(search, new_filename)
                    elif algo == "hc":
                        # Send in budget -1 because the initial state evaluation isn't included in the budget
                        search = hcOpt(app, system, datasize, budget-1, parent_dir, types, sizes, number_of_nodes)
                    elif algo == "sa":
                        search = saOpt(app, system, datasize, budget-1, parent_dir, types, sizes, number_of_nodes)


                    if algo != "bo":
                        getResult(search, filename)



# search = boGPyOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
