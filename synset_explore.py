import pdb
from nltk.corpus import wordnet as wn


def get_synset(term):
    return wn.synsets(term)


hypo = lambda s: s.hyponyms()
hyper = lambda s: s.hypernyms()

while 1:
    temp = get_synset('man')[0]
    #temp.lch_similarity(temp)
    word = raw_input('word:   ')
    word_list = get_synset(word)

    family = set()
    for word in word_list:
        hypo_family = set([i for i in word.closure(hypo)])
        hyper_family = set([i for i in word.closure(hyper)])
        this_family = hypo_family | hyper_family
        family |= this_family
    
    #sorted(similarity_idx.items(), key=operator.itemgetter(1))
    family = [str(member)[8:-2] for member in family]
    pdb.set_trace()
    
