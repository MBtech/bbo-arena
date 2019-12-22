# Algorithms and Libraries
- Random Search: Manually implemented
- LHS Search: using [pyDOE](https://pythonhosted.org/pyDOE/randomized.html)
- SMAC: using [pysmac](https://pysmac.readthedocs.io/en/latest/quickstart.html). Check out the [detailed API documentation](https://pysmac.readthedocs.io/en/latest/pysmac.html) to see if any advance settings need to be modified
- TPE: using hyperopt
- BO: using skopt
- Stochastic Hill climbing: using Solid
- Simulated Annealing: using Solid

# Other Options:
- Grid Search: sklearn (Exhaustive)
- Random Search: sklearn (Specific random distribution). Also available in Hyperopt
- BO with GPy: [GPyOpt](https://gpyopt.readthedocs.io/en/latest/#)

## Notes:
- As far as I know Skopt uses random sampling. Sobol sampling has been discussed in the github issues but it hasn't been included yet.

- Skopt seems to offer integer and categorical variables but it seems like the acquisition function still picks same configurations again and again. That's why I have shifted to the ask and tell interface.

- With current implementation using Skopt, I am using `sampling` as acquisition optimizer because the search space is small and essentially the whole search space is evaluated by the acquisition function. In order to not evaluate the values that have already been explored by the optimizer, I have made small change to the SkOpt library as well. Those changes need to be committed into a fork of SkOpt.
