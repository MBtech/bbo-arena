from Solid.TabuSearch import TabuSearch
import numpy as np
import copy
import sys
import json

def get_runtime(parent_dir, app, system, datasize, type, size, num):
    print(type, size, num)
    dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
    jsonName= dir + 'report.json'
    report = json.load(open(jsonName, 'r'))
    print(float(report["elapsed_time"]))
    return float(report["elapsed_time"])
    
## Resource oblivious hill climbing
## Neighbors aren't selected based on step increase in resources
class Algorithm(TabuSearch):
    count = 0
    parent_dir = '../scout/dataset/osr_multiple_nodes/'
    types = [ "c4", "m4", "r4"]
    sizes = ["large", "xlarge", "2xlarge"]
    node_sizes = {
        'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
        'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
        '2xlarge': [4, 6, 8, 10, 12]
    }
    app =''
    system =''
    datasize = ''

    def __init__(self, initial_state, tabu_size, max_steps, app, system, datasize):
        super().__init__(initial_state, tabu_size, max_steps)
        self.app = app
        self.system = system
        self.datasize=datasize

    def _neighborhood(self):
        state = self.current
        neighborhood = list()
        for key in state.keys():
            if key == "type":
                family = state["type"]
                size = state["size"]
                ind = self.types.index(family)
                if ind-1 >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = self.types[ind-1]
                    neighbor["size"] = size
                    neighborhood.append(neighbor)
                if ind+1 < len(self.types):
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = self.types[ind+1]
                    neighbor["size"] = size
                    neighborhood.append(neighbor)
            elif key=="size":
                family = state["type"]
                size = state["size"]
                ind = self.sizes.index(size)
                if ind-1 >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = family
                    neighbor["size"] = self.sizes[ind-1]
                    neighbor["num_nodes"] = self.node_sizes[self.sizes[ind-1]][self.node_sizes[size].index(state["num_nodes"])]
                    neighborhood.append(neighbor)
                if ind+1 < len(self.sizes):
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = family
                    neighbor["size"] = self.sizes[ind+1]
                    neighbor["num_nodes"] = self.node_sizes[self.sizes[ind+1]][self.node_sizes[size].index(state["num_nodes"])]
                    neighborhood.append(neighbor)
            else:
                family = state["type"]
                size = state["size"]
                ind = self.node_sizes[size].index(state["num_nodes"])
                if ind-1 >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["num_nodes"] = self.node_sizes[size][ind-1]
                    neighborhood.append(neighbor)
                if ind+1 < len(self.node_sizes[size]):
                    neighbor = copy.deepcopy(state)
                    neighbor["num_nodes"] = self.node_sizes[size][ind+1]
                    neighborhood.append(neighbor)
        return neighborhood

    def _score(self, state):
        self.count+=1
        print("Total Executions: " + str(self.count))
        print(state)
        runtime = get_runtime(self.parent_dir, self.app, self.system, self.datasize,
                state["type"], state["size"], state["num_nodes"])
        print(runtime)
        return -(runtime)

def test_algorithm(app, system, datasize):
    state = {"type": "m4", "size": "large" ,"num_nodes": 4}
    algorithm = Algorithm(state, 5, 15, app, system, datasize)
    best_solution, best_objective_value = algorithm.run()
    print(best_solution)
    print(best_objective_value)

app, system = sys.argv[1], sys.argv[2]
datasize = "huge"
test_algorithm(app, system, datasize)
