import sys
from models import models
import json
import os
import time
import pandas as pd

number_of_nodes = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
sizes = ['large', 'xlarge', '2xlarge']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark
config = json.load(open(sys.argv[1], 'r'))

budget = config["budget"]

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            data = list()
            for algo in config["bbo_algos"]:
                filename = system + '_' + app + '_' + datasize + '_' + algo
                if algo == "bo":
                    for estimator in config["bo_estimators"]:
                        for acq_method in config["bo_acq"][estimator]:
                            new_filename = filename + '_' + estimator + '_' + acq_method
                            print(new_filename)
                            m = models(new_filename, app, system, datasize, budget, parent_dir, types, sizes, number_of_nodes, optimizer=estimator, initial_samples=6, acquisition_method=acq_method)
                            # print(new_filename)
                            d = m.buildModel()
                            ae = d['ae']
                            mae = d['mae']
                            mse = d['mse']
                            rmse = d['rmse']
                            for e1, e2, e3, e4 in zip(ae, mae, mse, rmse):
                                data.append([ e1, e2, e3, e4, algo+'_'+estimator+'_'+acq_method])

            df = pd.DataFrame(data, columns=['ae', 'mae', 'mse', 'rmse', 'algorithm'])
            
            errorFilename = 'error/'+'error_'+system + '_' + app + '_' + datasize+'.csv'
            if os.path.isfile(errorFilename):
                df_read = pd.read_csv(errorFilename, index_col=False)
                df = df.append(df_read)

            df.to_csv(errorFilename, index=False)