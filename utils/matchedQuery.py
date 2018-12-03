class MatchedQuery:
    def __init__(self,query,approximate,match):
        #query: (('man', 1), ('in', 6), ('truck', 2))
        #approximate: a RankedRelation
        #match: [211651, 209964, 211650]
        self.query = query
        self.approximate = approximate
        self.imageNodeIds = tuple(match)
        self.setSimilarity()
    def getQuery(self):
        return self.query
    def getApproximate(self):
        return self.approximate
    def getImageNodeIds(self):
        return self.imageNodeIds
    def setSimilarity(self):
        #self.subject_similarity = (1.0-self.cos_sim(synset_embeddings[self.approximate.getModel()[0]][0],self.query.getSubjectEmbedding()[0]))/2.
        #self.object_similarity = (1.-self.cos_sim(synset_embeddings[self.approximate.getModel()[2]][0],self.query.getObjectEmbedding()[0]))/2.
        #self.relation_similarity = (1.-self.cos_sim(synset_embeddings[self.approximate.getModel()[1]][0],self.query.getRelationEmbedding()[0]))/2.
        self.similarity=[self.approximate.subjSim,self.approximate.objSim,self.approximate.predSim]
    #def cos_sim(self,a,b):
    #    return dot(a, b)/(norm(a)*norm(b))