class RankedRelation:
    def __init__(self,model,relation, rank):
        self.model=model
        self.relation=relation
        self.rank=rank
    def getRank(self):
        return self.rank
    def getModel(self):
        return self.model
    def getRelation(self):
        return self.relation