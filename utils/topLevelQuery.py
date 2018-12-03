import numpy as np
class TopLevelQuery:
    def __init__(self,query):
        #query: (('man', 1), ('in', 6), ('truck', 2))
        self.query = query
        self.baseQuery = tuple([item[0] for item in self.query])
        self.baseNodeIds = tuple([item[1] for item in self.query])
        self.subject_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        self.object_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        self.relation_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
    def setEmbeddings(self,embeddings=None):
        if self.baseQuery[0] in embeddings:
            self.subject_embedding = embeddings[self.baseQuery[0]].reshape(1,-1)
        else:
            self.subject_embedding = np.ones(300).reshape(1,-1)
        if self.baseQuery[1] in embeddings:
            self.relation_embedding = embeddings[self.baseQuery[1]].reshape(1,-1)
        else:
            self.relation_embedding = np.ones(300).reshape(1,-1)
        if self.baseQuery[2] in embeddings:
            self.object_embedding = embeddings[self.baseQuery[2]].reshape(1,-1)
        else:
            self.object_embedding = np.ones(300).reshape(1,-1)

        #self.subject_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        #self.object_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        #self.relation_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
    def getSubjectEmbedding(self):
        return self.subject_embedding
    def getObjectEmbedding(self):
        return self.object_embedding
    def getRelationEmbedding(self):
        return self.relation_embedding