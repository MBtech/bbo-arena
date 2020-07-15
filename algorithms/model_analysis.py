import sys
from models import models
from baseline import baseline
import json
import os
import time
import pandas as pd

parent_dir = {'s': '../scout/dataset/osr_multiple_nodes/', 'l': '../experiments/dataset/'}
number_of_nodes = { 's':
    {   
    'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
    'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
    '2xlarge': [4, 6, 8, 10, 12]
    },
    'l': {
    'large': [16, 24, 32, 40, 48, 56, 64],
    'xlarge': [8, 12, 16, 20, 24, 28, 32],
    '2xlarge': [4, 6, 8, 10, 12, 14, 16], 
    '4xlarge': [2, 3, 4, 5, 6, 7, 8]
    }
}
types = {'s': ['m4', 'c4', 'r4'], 'l': ['m5', 'm5a', 'c5', 'c5n', 'r5'] }
sizes = {'s': ['large', 'xlarge', '2xlarge'], 'l': ['large', 'xlarge', '2xlarge', '4xlarge']}

config = json.load(open(sys.argv[1], 'r'))
init_samples = config["initial_samples"]
budget = config["budget"]
dataset = config["dataset"]
metric = config["metric"]

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            data = list()
            for algo in config["bbo_algos"]:
                filename = system + '_' + app + '_' + datasize + '_' + algo
                if "bo" in algo:
                    for estimator in config["bo_estimators"]:
                        for acq_method in config["bo_acq"][estimator]:
                            if 'gp_hedge' in acq_method:
                                new_filename = filename + '_' + str(config["bo_args"]["xi"]) + '_' + str(config["bo_args"]["kappa"]) + '_' \
                                            + estimator + '_' + acq_method
                            elif 'LCB' in acq_method: 
                                new_filename = filename + '_' + str(config["bo_args"]["kappa"]) + '_' + estimator + '_' + acq_method
                            else:
                                new_filename = filename + '_' + str(config["bo_args"]["xi"]) + '_' + estimator + '_' + acq_method
                            print(new_filename)
                            m = models(new_filename, app, system, datasize, budget, parent_dir[dataset], types[dataset], sizes[dataset], 
                                        number_of_nodes[dataset], optimizer=estimator, initial_samples=init_samples, 
                                        acquisition_method=acq_method, metric=metric)
                            # print(new_filename)
                            d = m.buildModel()
                            ae = d['ae']
                            mae = d['mae']
                            mse = d['mse']
                            rmse = d['rmse']
                            for e1, e2, e3, e4 in zip(ae, mae, mse, rmse):
                                data.append([ e1, e2, e3, e4, algo+'_'+estimator+'_'+acq_method])
                
                elif "random" in algo:
                    new_filename = ''
                    m = baseline(new_filename, app, system, datasize, budget, parent_dir[dataset], types[dataset], sizes[dataset], 
                        number_of_nodes[dataset], metric=metric)
                    d = m.buildModel()
                    ae = d['ae']
                    mae = d['mae']
                    mse = d['mse']
                    rmse = d['rmse']
                    for e1, e2, e3, e4 in zip(ae, mae, mse, rmse):
                        data.append([ e1, e2, e3, e4, 'baseline'])

            df = pd.DataFrame(data, columns=['ae', 'mae', 'mse', 'rmse', 'algorithm'])
            
            # print(df)
            errorFilename = 'error/'+ config["metric"] +'_error_'+system + '_' + app + '_' + datasize+'.csv'
            if os.path.isfile(errorFilename):
                df_read = pd.read_csv(errorFilename, index_col=False)
                df = df.append(df_read)

            df.to_csv(errorFilename, index=False)