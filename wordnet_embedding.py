'''
This file generates the word2vec embeddings for wordnet.

We assume you have the gensim library installed, and the Google news vectors available.
We also assume you have wordnet corpus installed.
'''
import pdb

w2v_path = 'GoogleNews-vectors-negative300.bin'
from gensim.models import KeyedVectors
from gensim.utils import tokenize
from numpy import zeros
import h5py
import os
import numpy as np

'''
from https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
'''
def save_dict_to_hdf5(dic, filename):
    """
    ....
    """
    with h5py.File(filename, 'w') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)

def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            raise ValueError('Cannot save %s type'%type(item))

def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans


model = KeyedVectors.load_word2vec_format(w2v_path, binary=True, unicode_errors='ignore')

from nltk.corpus import wordnet as wn
import time

start = time.time()
local = time.time()
wn_embedding = {}
zero_v = zeros(shape=(300,))
counter = 0
all_syn = [item for item in wn.all_synsets()]
for _synset in all_syn:
    score = zeros(shape=(300,))
    lemma_names = [item.name() for item in _synset.lemmas()]
    for _name in lemma_names:
        score+= model[_name] if _name in model else zero_v
    wn_embedding[str(_synset)[8:-2]] = score/float(len(lemma_names))
    counter+=1

    if counter%1000 == 0:
        print "Completed %7i/%7i in %4.2f (this round took %4.2fs)" % (counter, len(all_syn), time.time()-start, time.time()-local)
        local = time.time()

save_dict_to_hdf5(wn_embedding, 'wn_embedding.h5')
