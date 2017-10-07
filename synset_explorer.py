import pdb
from nltk.corpus import wordnet as wn
import sqlite3
import operator

#We need to limit the info we send back
class WordFamily:
    def __init__(self,word):
        self.word = word
        self.topLevelFamily=[]
        self.hypoRanks=[]
        self.hyperRanks=[]
    def setTopLevel(self,topLevel):
        self.topLevelFamily = topLevel
    def setHypoRanks(self,hypoRanks):
        self.hypoRanks=hypoRanks
    def setHyperRanks(self,hyperRanks):
        self.hyperRanks=hyperRanks
    def getTopLevel(self):
        return self.topLevelFamily
    def getHyperRanks(self):
        return self.hyperRanks
    def getHypoRanks(self):
        return self.hypoRanks
    def getWord(self):
        return self.word
    def createRankings(self):
        self.baseHypoRanking=self.getBaseRanking()[:].extend(self.getHypoRanks())
        self.baseHyperRanking=self.getBaseRanking()[:].extend(self.getHyperRanks())
        self.fullRanking = self.getBaseHypoRanking()[:].extend(self.getHyperRanks())

    def getBaseRanking(self):
        return self.topLevelFamily
    def getBaseHyperRanking(self):
        return self.baseHyperRanking
    def getBaseHypoRanking(self):
        return self.baseHypoRanking
    def getFullRanking(self):
        return self.fullRanking

class SynsetExplorer:
    
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
    #Sort by distance
    def reduce(self,inputList,rankingCount):
        setVerify={}
        returnList=[]
        for item in inputList:
            if item in rankingCount and item not in setVerify:
                returnList.append(item)
                setVerify[item]=1
        return returnList
    def sort(self,rankedList):
        return [sortItem[0] for sortItem in sorted([item for subList in rankedList for item in subList],key=lambda x:x[1],reverse=True)]

    def updateRankings(self,rankList, setVerify, inputList, rankingCount):
        for entry in inputList:
            if entry not in setVerify:
                rankList.append((entry,rankingCount[entry]))
                setVerify[entry]=1

    def explore(self,word):
        node = WordFamily(word)
        wordList = self.get_synset(self.cleaned(node.getWord()))
        family, hypoRanks, hyperRanks = self.get_family_rankings(wordList)
        topLevels = self.synset_extract(wordList)
        familySynsetCounts = self.get_counts(family)
        topLevelSynsetCounts = self.get_counts(topLevels)

        setVerify={}
        rankList = []

        node.setTopLevel(self.reduce(topLevels))
        node.setHypoRanks(self.reduce(self.sort(hypoRanks),familySynsetCounts))
        node.setHyperRanks(self.reduce(self.sort(hyperRanks),familySynsetCounts))
    
        node.createRankings()
        
        return node
        