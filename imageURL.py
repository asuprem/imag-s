import json

class ImageURL():
    def __init__(self, file_name):
        with open(file_name,'r') as file_:
            self.mapper = json.loads(file_.read().strip())

    def getURL(self,id_):
        if isinstance(id_,int):
            return self.mapper[str(id_)]
        else:
            return self.mapper[id_]
    #list of ids
    def getURLs(self,ids):
        if isinstance(ids[0],int):
            return [self.mapper[str(id_)] for id_ in ids]
        else:
            return [self.mapper[id_] for id_ in ids]