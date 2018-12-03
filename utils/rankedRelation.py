class RankedRelation:
    def __init__(self,model,relation, rank):
        self.model=model
        self.relation=relation
        self.rank=rank[3]
        self.subjSim = rank[0]
        self.objSim = rank[1]
        self.predSim = rank[2]
    def getRank(self):
        return self.rank
    def getModel(self):
        return self.model
    def getRelation(self):
        return self.relation