from abc import ABC, abstractmethod

class optimizer(ABC):
    def __init__(self, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes):
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

    def convertToConfig(self, x):
        pass

    @abstractmethod
    def getRuntime(self, x1, x2, x3):
        pass

    @abstractmethod
    def runOptimizer(self):
        pass
