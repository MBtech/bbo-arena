# bbo-arena

## Blackbox optimization algorithms (under test)
- SMAC -> There is a problem with SMAC on MacOS
- CMA-ES -> CMA-ES doesn't seem to have bounds on the search space and it is designed completely for a continuous search space
- GpyOpt -> Working
- HyperOpt -> Working
- Solid -> StochasticHillClimb(Done), Others (In progress)

**Note on Solid**
Solid hasn't been updated for Python3. However, I am working on an implementation to transition the project to Python3.
Both tabu search and simulated annealing do more function evaluations that the maximum number of steps

## Installation
Since I have included scout repo as a submodule if you clone this repo use

`git clone --recurse-submodules https://github.com/MBtech/bbo-arena.git`

Make sure you have python 3.5.2 or above installed on your system
If you are on mac make sure that you have xcode tools installed using

`xcode-select --install`


`apt-get install swig` or `brew install swig@3` if you are on mac. Make sure you have swig 3 and not version 4.

`pip install cython smac[all] cma gpyopt hyperopt solidpy`

## TODO:
- The libraries need to be modified in case of continuous optimization algorithms cases so that same configurations aren't counted twice.
- Fix the max number of step case for tabu search and for SimulatedAnnealing since max steps don't equal max function evaluations.
