import pdb
from nltk.corpus import wordnet as wn
import sqlite3
import operator

class Synset_Explorer:
    
    def __init__(self,database_file):
        self.conn = sqlite3.connect(database_file)
        self.cursor = self.conn.cursor()
        self.hypo = lambda s: s.hyponyms()
        self.hyper = lambda s: s.hypernyms()
        self.initialize()
    def get_synset(self,term):
        return wn.synsets(term)
    def initialize(self):
        temp = self.get_synset('man')[0]
        temp.lch_similarity(temp)

    def get_mains(self,word_list):
        return [str(member)[8:-2] for member in word_list]

    def get_counts(self, word_set):
        return dict(self.cursor.execute(\
                'Select synset,count from synset_count where synset in ({0})'\
                .format(', '.join('?' for _ in word_set)), word_set)\
                .fetchall())

    def closure(self, word, closure_function):
        return set([i for i in word.closure(closure_function)])
    def ranking(self, word, family):
        return {str(i)[8:-2]:word.lch_similarity(i) for i in family}
    def ranking_sort(self,rank_list):
        return sorted(rank_list.items(), key=operator.itemgetter(1), reverse=True)
    def synset_extract(self,synsets):
        return [str(synset)[8:-2] for synset in synsets]
    def get_family_rankings(self, word_list):
        hypo_extended, hyper_extended = set(), set()
        hypo_ranks, hyper_ranks = [],[]
        family = set()

        for word in word_list:
            hypo_family = self.closure(word, self.hypo)
            hyper_family = self.closure(word, self.hyper)

            hypo_extended |= hypo_family
            hyper_extended |= hyper_family

            family |= hypo_family
            family |= hyper_family

            hypo_ranking = self.ranking(word,hypo_family)
            hyper_ranking = self.ranking(word, hyper_family)

            hypo_ranks.append(self.ranking_sort(hypo_ranking))
            hyper_ranks.append(self.ranking_sort(hyper_ranking))

        family_list = self.synset_extract(family)
        return family_list, hypo_ranks, hyper_ranks

    def cleaned(self,word):
        return word.replace(' ','_')
    def sort(self,rankedList):
        return [sortItem[0] for sortItem in sorted([item for subList in rankedList for item in subList],key=lambda x:x[1],reverse=True)]

    def updateRankings(self,rankList, setVerify, inputList, rankingCount):
        for entry in inputList:
                if entry in rankingCount and entry not in setVerify:
                    rankList.append((entry,rankingCount[entry]))
                    setVerify[entry]=1

    def explore(self,word):
        wordList = self.get_synset(self.cleaned(word))
        family, hypoRanks, hyperRanks = self.get_family_rankings(wordList)
        topLevels = self.synset_extract(wordList)
        familySynsetCounts = self.get_counts(family)
        topLevelSynsetCounts = self.get_counts(topLevels)

        setVerify={}
        rankList = []

        hypoRanks = self.sort(hypoRanks)
        hyperRanks = self.sort(hyperRanks)
        self.updateRankings(rankList,setVerify,topLevels, topLevelSynsetCounts)
        self.updateRankings(rankList,setVerify,hypoRanks, familySynsetCounts)
        self.updateRankings(rankList,setVerify,hyperRanks, familySynsetCounts)

        return [entry[0] for entry in rankList]
        