from Solid.StochasticHillClimb import StochasticHillClimb
import numpy as np
import copy
import sys
import json
from optimizer import optimizer

def get_runtime(parent_dir, app, system, datasize, type, size, num):
    # print(type, size, num)
    dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
    jsonName= dir + 'report.json'
    report = json.load(open(jsonName, 'r'))
    # print(float(report["elapsed_time"]))
    return float(report["elapsed_time"])

def closest(lst, K):

    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
## Resource oblivious hill climbing
## Neighbors aren't selected based on step increase in resources
class Algorithm(StochasticHillClimb):
    def __init__(self, initial_state, temp, max_steps, app, system, datasize,
                    parent_dir, number_of_nodes,types, sizes):
        super().__init__(initial_state, temp, max_steps)
        self.app = app
        self.system = system
        self.datasize=datasize
        self.parent_dir = parent_dir
        self.number_of_nodes = number_of_nodes
        self.types = types
        self.sizes = sizes
        self.trials = list()
        self.results = list()

    def neighborhood(self, state, step=1):
        neighborhood = list()
        for key in state.keys():
            if key == "type":
                family = state["type"]
                size = state["size"]
                ind = self.types.index(family)
                if ind-step >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = self.types[ind-step]
                    neighbor["size"] = size
                    neighborhood.append(neighbor)
                if ind+step < len(self.types):
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = self.types[ind+step]
                    neighbor["size"] = size
                    neighborhood.append(neighbor)
            elif key=="size":
                family = state["type"]
                size = state["size"]
                ind = self.sizes.index(size)
                if ind-step >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = family
                    neighbor["size"] = self.sizes[ind-step]
                    neighbor["num"] = closest(self.number_of_nodes[self.sizes[ind-step]], state["num"]*(2*step))
                    neighborhood.append(neighbor)
                if ind+step < len(self.sizes):
                    neighbor = copy.deepcopy(state)
                    neighbor["type"] = family
                    neighbor["size"] = self.sizes[ind+step]
                    neighbor["num"] = closest(self.number_of_nodes[self.sizes[ind+step]], state["num"]/(2*step))
                    neighborhood.append(neighbor)
            else:
                family = state["type"]
                size = state["size"]
                ind = self.number_of_nodes[size].index(state["num"])
                if ind-step >= 0:
                    neighbor = copy.deepcopy(state)
                    neighbor["num"] = self.number_of_nodes[size][ind-step]
                    neighborhood.append(neighbor)
                if ind+step < len(self.number_of_nodes[size]):
                    neighbor = copy.deepcopy(state)
                    neighbor["num"] = self.number_of_nodes[size][ind+step]
                    neighborhood.append(neighbor)
        return neighborhood

    def randomPoint(self):
        state = dict()
        state["type"]= np.random.choice(self.types)
        state["size"]= np.random.choice(self.sizes)
        state["num"]= np.random.choice(self.number_of_nodes[state["size"]])
        return state

    def _neighbor(self):
        neighbors = self.neighborhood(self.current_state)
        neighbors = [neighbor for neighbor in neighbors if neighbor not in self.trials ]
        if len(neighbors) ==0:
            state = self.randomPoint()
            while state in self.trials:
                state = self.randomPoint()
            return state
        return neighbors[np.random.choice(len(neighbors), 1)[0]]

    def _objective(self, state):
        # df = self.df
        if state in self.trials:
            return self.results[self.trials.index(state)]
        else:
            # print(state)
            runtime = get_runtime(self.parent_dir, self.app, self.system, self.datasize,
                    state["type"], state["size"], state["num"])
            self.trials.append(state)
            self.results.append(-(runtime))
            return -(runtime)

class hcOpt(optimizer):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes,
                            number_of_nodes, temp = 100,
                            init_state={"type": "m4", "size": "large" ,"num": 4}):
        super(hcOpt, self).__init__(app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes)
        self.init_state = init_state
        self.temp = temp

    def getRuntime(self):
        pass

    def runOptimizer(self):
        algorithm = Algorithm(self.init_state, self.temp, self.budget, self.app,
                    self.system, self.datasize, self.parent_dir, self.number_of_nodes, self.types, self.sizes)
        best_parameters, value = algorithm.run()
        print(-value, best_parameters)
        return {'value': -value, 'params': best_parameters}