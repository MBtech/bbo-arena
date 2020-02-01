import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
from utils import getAll
import sys
import numpy as np
import math

sns.set(style="whitegrid")
if len(sys.argv) > 1:
    configJsonName = sys.argv[1]
    prefix = sys.argv[2]
else:
    configJsonName = "test_configs/all_runs.json"
    prefix = "opt"


config = json.load(open(configJsonName, 'r'))
count = 0
good_confs = list()
all_runtimes = list()

for system in config["systems"]:
    for app in config["applications"][system]:
        for datasize in config["datasizes"]:
            plt.figure()
            title = system+"_"+app+"_"+datasize

            runtimes = getAll(app, system, datasize)
            
            df = pd.DataFrame(runtimes, columns = ['Runtime', 'Num', 'Type', 'Size'])
            df_norm = df.copy()
            df_norm['Runtime'] = df['Runtime']/df['Runtime'].min()
            max_runtime = df['Runtime'].max()
            r = max_runtime / df['Runtime'].min()
            print(r)

            min_runtime = df['Runtime'].min()
            runtime_threashold = 1.1*min_runtime
            good_confs.append([title, len(df[df['Runtime']<=runtime_threashold])])

            for runtime in runtimes:
                runtime.append(title)
                all_runtimes.append(runtime)

            # sns.distplot(np.array(df['Runtime']), kde=False, rug=True)

            kwargs = {'cumulative': True}
            # sns.distplot(df['Runtime'].to_numpy(), hist_kws=kwargs, kde_kws=kwargs)


            plt.hist(df_norm['Runtime'].to_numpy(), cumulative=True, density=True, bins=int(math.ceil((r-1)*10)))
            plt.xlim(1, min(r, 5))
            plt.savefig('plots/data/cdf_'+ title + '.pdf', bbox_inches = "tight")

            plt.figure()
            # sns.kdeplot(df['Runtime'].to_numpy())
            sns.distplot(np.array(df['Runtime']), kde=True, rug=True)
            plt.savefig('plots/data/pdf_'+ title + '.pdf', bbox_inches = "tight")
            # plt.title(title)
            # plt.legend(loc='upper right', ncol=2, prop={'size': 9})
            # plt.savefig('plots/data/'+ title + '.pdf', bbox_inches = "tight")
            # plt.show()
            # sys.exit()

plt.figure()
df_runtimes = pd.DataFrame(all_runtimes, columns = ['Runtime', 'Num', 'Type', 'Size', 'Workload'])
sns.boxplot(x='Workload', y='Runtime', data=df_runtimes)
plt.xticks(rotation=90)
plt.savefig('plots/data/runtimes.pdf', bbox_inches = "tight")
# plt.show()
print(df_runtimes.groupby('Workload')['Runtime'].describe())
print(df_runtimes.groupby('Workload')['Runtime'].describe()['max']/df_runtimes.groupby('Workload')['Runtime'].describe()['min'])

df_confs = pd.DataFrame(good_confs, columns=['Workload', 'No. of Good Confs'])
print(df_confs)
print(np.median(df_confs['No. of Good Confs']))