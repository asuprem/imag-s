import pdb
from nltk.corpus import wordnet as wn
import sqlite3
import operator



#We need to limit the info we send back
class WordFamily:
    def __init__(self,word):
        self.word = word
        self.sisters=[]
        self.hypoRanks=[]
        self.hyperRanks=[]
    def setSisters(self,sisters):
        self.sisters = sisters
    def setHypoRanks(self,hypoRanks):
        hypoRanks = [item for item in hypoRanks if item not in self.getSisters()]
        self.hypoRanks=hypoRanks
    def setHyperRanks(self,hyperRanks):
        hyperRanks = [item for item in hyperRanks if item not in self.getSisters()]
        self.hyperRanks=hyperRanks
    def getSisters(self):
        return self.sisters
    def getHyperRanks(self):
        return self.hyperRanks
    def getHypoRanks(self):
        return self.hypoRanks
    def getWord(self):
        return self.word
    def createRankings(self):
        self.baseHypoRanking=self.getBaseRanking()+self.getHypoRanks()
        self.baseHyperRanking=self.getBaseRanking()+self.getHyperRanks()
        self.fullRanking = self.getBaseHypoRanking()+self.getHyperRanks()

    def getBaseRanking(self):
        return self.sisters
    def getBaseHyperRanking(self):
        return self.baseHyperRanking
    def getBaseHypoRanking(self):
        return self.baseHypoRanking
    def getFullRanking(self):
        return self.fullRanking
    def setFamilySynsetCounts(self,familySynsetCounts):
        self.familySynsetCounts=familySynsetCounts
    def setSisterSynsetCounts(self,sisterSynsetCounts):
        self.sisterSynsetCounts=sisterSynsetCounts
    def getFamilySynsetCounts(self):
        return self.familySynsetCounts
    def getSisterSynsetCounts(self):
        return self.sisterSynsetCounts
class SynsetExplorer:
    
    def __init__(self,database_file):
        self.conn = sqlite3.connect(database_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.hypo = lambda s: s.hyponyms()
        self.hyper = lambda s: s.hypernyms()
        #self.initialize()
    def get_synset(self,term):
        return wn.synsets(term)
    def initialize(self):
        temp = self.get_synset('man')[0]
        temp.wup_similarity(temp)

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
        return {str(i)[8:-2]:word.wup_similarity(i) for i in family}
    def ranking_sort(self,rank_list):
        return sorted(rank_list.items(), key=operator.itemgetter(1), reverse=True)
    def synset_extract(self,synsets):
        return [str(synset)[8:-2] for synset in synsets]
    def get_family_rankings(self, _synset_list):
        hypo_extended, hyper_extended = set(), set()
        hypo_ranks, hyper_ranks = [],[]
        family = set()
        #this gets the extended hypo and hypernims of the source natural word's synsets <---- PLURAL
        for _synset in _synset_list:
            #hypo_family = self.closure(word, self.hypo)
            #hyper_family = self.closure(word, self.hyper)
            #hypo are child synsets
            hypo_family = set(_synset.hyponyms())
            #hyper are parent synsets
            hyper_family = set(_synset.hypernyms())
            #extend the set for each synset of the source natural word
            hypo_extended |= hypo_family
            hyper_extended |= hyper_family
            #add both hypo and hypeer to family - which is the parent and child synsets of all sister synsets of source natural word
            family |= hypo_family
            family |= hyper_family

            #here, wup similarity between source ntural word synset and all synsets in child family <--- TODO convert to w2v
            hypo_ranking = self.ranking(_synset,hypo_family)
            hyper_ranking = self.ranking(_synset, hyper_family)
            #sort the ranks and append them to hypo/hyper_ranks in sourted order (sorted in decending order <--- larger is more similar)
            hypo_ranks.append(self.ranking_sort(hypo_ranking))
            hyper_ranks.append(self.ranking_sort(hyper_ranking))
        #get just the natural synset, instead of object, i.e. Synset('adonis.n.01') --> 'adonis.n.01'
        family_list = self.synset_extract(family)
        #spdb.set_trace()
        return family_list, hypo_ranks, hyper_ranks

    def cleaned(self,word):
        return word.replace(' ','_')
    #Sort by distance
    def _reduce(self,inputList,rankingCount):
        setVerify={}
        returnList=[]
        for item in inputList:
            if item in rankingCount and item not in setVerify:
                returnList.append(item)
                setVerify[item]=1
        return returnList
    def sort(self,rankedList):
        return [sortItem[0] for sortItem in sorted([item for subList in rankedList for item in subList],key=lambda x:x[1],reverse=True)]

    '''
    def updateRankings(self,rankList, setVerify, inputList, rankingCount):
        for entry in inputList:
            if entry not in setVerify:
                rankList.append((entry,rankingCount[entry]))
                setVerify[entry]=1
    '''
    def explore(self,word):
        node = WordFamily(word)
        wordList = self.get_synset(self.cleaned(node.getWord()))
        #see comments inside function
        family, hypoRanks, hyperRanks = self.get_family_rankings(wordList)
        sisters = self.synset_extract(wordList)
        #this is the number of times the synset exists?
        #toplevel vs Family --> toplevel is sister; family is everything
        node.setFamilySynsetCounts(self.get_counts(family))
        node.setSisterSynsetCounts(self.get_counts(sisters))

        #setVerify={}
        rankList = []
        #so for each hypoRank/toplevel, if it is in the Family or sisters, then set() it
        node.setSisters(self._reduce(sisters, node.getSisterSynsetCounts()))
        node.setHypoRanks(self._reduce(self.sort(hypoRanks),node.getFamilySynsetCounts()))
        node.setHyperRanks(self._reduce(self.sort(hyperRanks),node.getFamilySynsetCounts()))
        #this creates baseHypo, Full, and BaseHyper Ranks
        node.createRankings()
        
        return node
