

from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
import pdb
class BaseModel:
    def __init__(self, subject, predicate, _object):
        #subjectFamily.getBaseRanking()[0], predicateFamily.getBaseRanking()[0], objectFamily.getBaseRanking()[0]
        self.natural_model = (subject.word,predicate.word,_object.word)
        self.model = (subject.getBaseRanking()[0], predicate.getBaseRanking()[0],_object.getBaseRanking()[0])
        self.subject = wn.synset(self.model[0])
        self.predicate = wn.synset(self.model[1])
        self.object = wn.synset(self.model[2])
    def synCompare(self,syn1,syn2):
        return syn1[-4:-3] == syn2[-4:-3]
    def rank(self,relation):
        subject = wn.synset(relation[0])
        predicate = wn.synset(relation[1])
        _object = wn.synset(relation[2])
        subjSimilarity, objSimilarity,predSimilarity = 1,1,1
        #so we will adjust this now to perform cos_sim. For this, we need the dictionary...
        if self.synCompare(self.model[0],relation[0]):
            subjSimilarity = self.subject.lch_similarity(subject)
        if self.synCompare(self.model[2],relation[2]):
            objSimilarity = self.object.lch_similarity(_object)
        if self.synCompare(self.model[1],relation[1]):
            predSimilarity = self.predicate.lch_similarity(predicate)
        if not predSimilarity:
            predSimilarity=1
        return subjSimilarity*predSimilarity*objSimilarity
    def getModel(self):
        return self.model