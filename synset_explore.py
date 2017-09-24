import pdb
from nltk.corpus import wordnet as wn
import sqlite3
import operator
import sys

conn = sqlite3.connect('../ExtractedData/' + sys.argv[1] + '.db')
sqCurs = conn.cursor()

def get_synset(term):
    return wn.synsets(term)


hypo = lambda s: s.hyponyms()
hyper = lambda s: s.hypernyms()
temp = get_synset('man')[0]
temp.lch_similarity(temp)
while 1:
    word = raw_input('word:   ')
    word_list = get_synset(word.replace(' ','_'))

    family = set()
    list_ranks=[]
    for word in word_list:
        hypo_family = set([i for i in word.closure(hypo)])
        hyper_family = set([i for i in word.closure(hyper)])
        this_family = hypo_family | hyper_family
        family |= this_family

        this_family.add(word)
        this_ranking = {i:word.lch_similarity(i) for i in this_family}
        list_ranks.append(sorted(this_ranking.items(), key=operator.itemgetter(1), reverse=True))

    #sorted(similarity_idx.items(), key=operator.itemgetter(1))
    family = [str(member)[8:-2] for member in family]
    mains = [str(member)[8:-2] for member in word_list]
    
    family_synset_counts = dict(sqCurs.execute('Select synset,count from synset_count where synset in ({0})'.format(', '.join('?' for _ in family)), family).fetchall())
    main_synset_counts = dict(sqCurs.execute('Select synset,count from synset_count where synset in ({0})'.format(', '.join('?' for _ in mains)), mains).fetchall())
    
    rank_list=[]
    in_dict={}

    for idx,word in enumerate(word_list):
        rank_dict={}
        print mains[idx] + ' : ' + str(main_synset_counts[mains[idx]] if mains[idx] in main_synset_counts else 0)
        if mains[idx] in main_synset_counts and mains[idx] not in in_dict:
            rank_list.append((mains[idx],main_synset_counts[mains[idx]]))
            in_dict[mains[idx]] = 1
        for l_idx, l_word in enumerate(list_ranks[idx]):
            l_str = str(l_word[0])[8:-2]
            print '     ' + l_str + ' : ' + str(family_synset_counts[l_str] if l_str in family_synset_counts else 0)
            if l_str in family_synset_counts and l_str not in in_dict:
                rank_dict[l_str] = family_synset_counts[l_str]
                in_dict[l_str] = 1
        rank_dict = sorted(rank_dict.items(), key=operator.itemgetter(1), reverse=True)
        rank_list.extend(rank_dict)

        #pdb.set_trace()
    print '\n\n'
    for entry in rank_list:
        print entry[0] + ' : ' + str(entry[1])



    print '\n\n\n-------------------------------\n'
    
