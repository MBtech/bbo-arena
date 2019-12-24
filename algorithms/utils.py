import pickle
import os

def pickleWrite(filename, data):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def pickleRead(filename, default=[]):
    if os.path.isfile(filename):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)
            return data
    else:
        return default
