

from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from scipy import spatial
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
    def rank(self,relation, embedder = None,w2vModel = None):
        subject = wn.synset(relation[0])
        predicate = wn.synset(relation[1])
        _object = wn.synset(relation[2])
        subjSimilarity, objSimilarity,predSimilarity = 1.,1.,1.
        #so we will adjust this now to perform cos_sim. For this, we need the dictionary...
        if self.synCompare(self.model[0],relation[0]):
            if embedder is not None and w2vModel is not None:
                #perform cos_sim between self.natural_model <-- nlp and subject <-- wn
                src=embedder[str(subject)[8:-2]]
                tgt=w2vModel[self.natural_model[0]]
                subjSimilarity = spatial.distance.cosine(src,tgt)
            else:
                subjSimilarity = self.subject.lch_similarity(subject)
        if self.synCompare(self.model[2],relation[2]):
            if embedder is not None and w2vModel is not None:
                #perform cos_sim between self.natural_model <-- nlp and subject <-- wn
                src=embedder[str(_object)[8:-2]]
                tgt=w2vModel[self.natural_model[2]]
                objSimilarity = spatial.distance.cosine(src,tgt)
            else:
                objSimilarity = self.object.lch_similarity(_object)
        if self.synCompare(self.model[1],relation[1]):
            if embedder is not None and w2vModel is not None:
                #perform cos_sim between self.natural_model <-- nlp and subject <-- wn
                src=embedder[str(predicate)[8:-2]]
                tgt=w2vModel[self.natural_model[1]]
                predSimilarity = spatial.distance.cosine(src,tgt)
            else:
                predSimilarity = self.predicate.lch_similarity(predicate)
        if not predSimilarity:
            predSimilarity=1.0
        return (subjSimilarity+predSimilarity+objSimilarity)/3.0
    def getModel(self):
        return self.model