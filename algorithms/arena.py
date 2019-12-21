import sys
from lhssearch import *
from randsearch import *
from smac import *
from tpe import *
from bogpyopt import *
from boskopt import boSkOpt
from hillclimbing import hcOpt
number_of_nodes = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark
app =sys.argv[1]
system = sys.argv[2]
datasize = 'huge'
budget = 15

# search = lhsSearch(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
# search = randSearch(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
# search = smac(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
# search = tpeOptimizer(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
# search = boGPyOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
# search = boSkOpt(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes,
#                     optimizer='RF', initial_samples=5, acquisition_method='EI')

# Send in budget -1 because the initial state evaluation isn't included in the budget
search = hcOpt(app, system, datasize, budget-1, parent_dir, types, sizes, number_of_nodes)
search.runOptimizer()
