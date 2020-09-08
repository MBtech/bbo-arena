# Notes

## Blackbox optimization libraries/algorithms (under test)
- SMAC -> Working using [pysmac](https://github.com/automl/pysmac) (There is a problem with [SMACv3](https://github.com/automl/SMAC3) on MacOS)
- [CMA-ES](https://github.com/CMA-ES/pycma) -> CMA-ES doesn't seem to have bounds on the search space and it is designed completely for a continuous search space
- [GpyOpt](https://github.com/SheffieldML/GPyOpt) -> Working
- [HyperOpt](https://github.com/hyperopt/hyperopt) -> Working
- [Solid](https://github.com/MBtech/Solid) -> StochasticHillClimb, SimulatedAnnealing, TabuSearch(Done), Others (In progress)
- [BBopt](https://github.com/evhub/bbopt) (Wrapper for Hyperopt and scikit optimize) -> Working


### Other potential algorithms/libraries
- Iterated local search
- Variable neighborhood search
- Guided local search
- Kriging Surrogate model ([Model based optimization library in R](https://github.com/mlr-org/mlrMBO))
- SVM Surrogate model
- [Optunity](https://optunity.readthedocs.io/en/latest/user/solvers.html)
- [Optuna](https://github.com/optuna/optuna)
- [Sherpa](https://github.com/sherpa-ai/sherpa)
- [shgo](https://stefan-endres.github.io/shgo/)

**Note on Solid**

Solid hasn't been updated for Python3. However, I am working on an implementation to transition the project to Python3.
Both tabu search and simulated annealing do more function evaluations than the maximum number of steps.

## Notes:
Single solution based [metaheuristics methods](https://en.wikipedia.org/wiki/Metaheuristic) are more appropriate for cloud configuration problem

Guided local search is a special case of tabu search.

Hill climbing (with restart) is a case of iterated local search.

Algorithms such as genetic algorithms and evolutionary algorithms are use multiple solutions aren't appropriate because of the number of samples they require to be useful.


## TODO:
- The libraries need to be modified in case of continuous optimization algorithms cases so that same configurations aren't counted twice.
- Fix the max number of step case for tabu search and for SimulatedAnnealing since max steps don't equal max function evaluations.

## Tutorials:
- [On using hyperopt: Advanced Machine Learning](https://blog.goodaudience.com/on-using-hyperopt-advanced-machine-learning-a2dde2ccece7)
- [Hyperparameter Optimization in Python](https://towardsdatascience.com/hyperparameter-optimization-in-python-part-0-introduction-c4b66791614b)

## Other readings: 
- [What does RMSE really mean?](https://towardsdatascience.com/what-does-rmse-really-mean-806b65f2e48e)
