import pickle
import os

def pickleWrite(filename, data):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def pickleRead(filename, default=[]):
    if os.path.isfile(filename):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)
        os.remove(filename)
        return data
    else:
        return default

def updatePickle(trial, filename='trials.pickle', default={'trials':[]}):
    trials = pickleRead(filename, default={'trials':[]})
    trials['trials'].append(trial)
    pickleWrite('trials.pickle', trials)
