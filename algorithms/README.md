# Algorithms and Libraries
- Random Search: Manually implemented
- LHS Search: using [pyDOE](https://pythonhosted.org/pyDOE/randomized.html)
- SMAC: using [pysmac](https://pysmac.readthedocs.io/en/latest/quickstart.html). Check out the [detailed API documentation](https://pysmac.readthedocs.io/en/latest/pysmac.html) to see if any advance settings need to be modified
- TPE: using hyperopt
- BO: using skopt

# Other Options:
- Grid Search: sklearn (Exhaustive)
- Random Search: sklearn (Specific random distribution). Also available in Hyperopt
- BO with GPy: [GPyOpt](https://gpyopt.readthedocs.io/en/latest/#)

## Notes:
As far as I know Skopt uses random sampling. Sobol sampling has been discussed in the github issues but it hasn't been included yet.
