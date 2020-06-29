"""
This script allows use to run a grid search over the selected values of the hyperparameters
"""

import subprocess
import json
import sys 
import itertools

config_filename = sys.argv[1]
config = json.load(open(config_filename, 'r'))
metric = "cost"

cmd = ["python", "arena.py", config_filename, metric]

algo = "bo_args"
# Starting from python 3.6 dict maintains insertion order
hyper_params = {"hc": {"temp": [50, 100, 250, 500, 750, 1000]},
                "sa": {"schedule_constant": [0.3, 0.5, 0.7, 0.9], "temp": [50, 100, 250, 500, 750, 1000]},
                "tpe_args": {"gamma": [0.1, 0.25, 0.4, 0.55, 0.7]},
                "bo_args": {
                    "xi": [0.01, 0.05, 0.1, 0.2],
                    "kappa": [1.0, 1.5, 1.96, 3.0, 5.0]
                    }
                }
n_init = [3, 6, 9]

for n in n_init:
    if "tpe" in algo or "bo" in algo:
        name = algo.split('_')[0] + '_' + str(n)
    else:
        name = algo + '_' + str(n)


    config["initial_samples"] = n
    # Generate permutation in the form of hyerparameter:value
    keys, values = zip(*hyper_params[algo].items())
    hyper_param_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
    # print(hyper_param_configs)
    for hyper_param_config in hyper_param_configs:
        config["bbo_algos"] = name
        for param in hyper_param_config:
            config["bbo_algos"] = config["bbo_algos"] + '_' + str(hyper_param_config[param]) 
            config[algo][param] = hyper_param_config[param]
        config["bbo_algos"] = [config["bbo_algos"]]
        json.dump(config, open(config_filename, 'w'), indent=4)

        subprocess.run(cmd)