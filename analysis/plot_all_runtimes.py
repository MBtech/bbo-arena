import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import json
import sys

configs = {
'large': [4, 6, 8, 10, 12, 16, 24, 32, 40, 48],
'xlarge': [4, 6, 8, 10, 12, 16, 20, 24],
'2xlarge': [4, 6, 8, 10, 12]
}
types = ['m4', 'c4', 'r4']
datasizes = ['huge', 'bigdata']
parent_dir = '../scout/dataset/osr_multiple_nodes/'

# python plot_all_runtimes.py pagerank spark1.5
app =sys.argv[1]
system = sys.argv[2]

runtimes = {'huge': [], 'bigdata': []}

for type in types:
    for size in configs.keys():
        for num in configs[size]:
            for datasize in datasizes:
                dir = parent_dir + str(num) + '_'+ type+'.'+size+ '_'+ app + "_" +system + "_" + datasize + "_1/"
                jsonName= dir + 'report.json'
                if os.path.exists(jsonName):
                    report = json.load(open(jsonName, 'r'))
                    runtimes[datasize].append(float(report["elapsed_time"]))
                else:
                    print("File doesn't exist " + jsonName)

# print runtimes

fig, ax = plt.subplots()
i=1
for key in runtimes.keys():
    print(np.array(runtimes[key])/np.min(runtimes[key])<1.1)
    print(np.min(runtimes[key]))
    plt.boxplot(np.array(runtimes[key])/np.min(runtimes[key]), positions=[i], widths=0.7)
    i+=1
plt.xlim(0, 3)
plt.xticks([1, 2], runtimes.keys())
plt.show()
