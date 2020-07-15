import seaborn as sns
import json
import pandas as pd
import matplotlib.pyplot as plt
import sys 
import os 

figlabels = {
    'Experiment': 'Initial\n Samples',
    'Init Samples': '# Samples',
    'temp': 'T',
    'Budget': 'Opt. Budget',
    'schedule_constant': r'$\alpha$',
    'xi': 'xi',
    'kappa': r'$\kappa$',
    'gamma': r'$\gamma$'
    }

def relabel(labels):
    return_labels = []
    for label in labels:
        return_labels.append(figlabels[label.get_text()])
    return return_labels

imp = sys.argv[1]

df = pd.read_csv('plots/importance/'+ imp +'.csv', header=0, names=['Hyper-parameters', 'Importance'])


plt.figure(figsize=(3,2))    
ax = sns.boxplot(x='Hyper-parameters', y='Importance',  data=df)
ax.set_xticklabels(relabel(ax.get_xticklabels()), fontsize=8)
dir = 'plots/importance/'
os.makedirs(dir, exist_ok=True)
# plt.show()
plt.savefig(dir + imp  + '.pdf', bbox_inches = "tight")
plt.close()