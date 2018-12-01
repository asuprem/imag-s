from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from itertools import product
import sqlite3
import json
import pdb
class BaseModel:
    def __init__(self, subject, predicate, _object):
        self.model = (subject, predicate,_object)
        self.subject = wn.synset(subject)
        self.predicate = wn.synset(predicate)
        self.object = wn.synset(_object)
    def synCompare(self,syn1,syn2):
        return syn1[-4:-3] == syn2[-4:-3]
    def rank(self,relation):
        subject = wn.synset(relation[0])
        predicate = wn.synset(relation[1])
        _object = wn.synset(relation[2])
        subjSimilarity, objSimilarity,predSimilarity = 1,1,1
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
    


def getApproximates(relations, objectFamilies, relationFamilies, driver):
    queryApproximates={}
    for relation in relations:
        #Get the explored synsets
        subjectFamily = objectFamilies.explore(relation[0])
        objectFamily = objectFamilies.explore(relation[2])
        predicateFamily = relationFamilies.explore(relation[1])
        #Get the cleaned up relations (i.e. without u'sdfdf' -> 'sdfdf')
        aggregate_relation_subject = synset_cleaned(subject_relations_approximates(subjectFamily.getBaseHypoRanking(),objectFamily.getBaseHypoRanking(), driver))
        aggregate_relation_object = synset_cleaned(object_relations_approximates(objectFamily.getBaseHypoRanking(),subjectFamily.getBaseHypoRanking(), driver))        
        #Get the unique relations and the predicate relations and convert to synset format (for lch similarity)
        aggregateSynsets = toSynset(unique_intersection(aggregate_relation_object,aggregate_relation_subject))
        #Get relationship ranks compared to the predicate family
        relationRanks = rankRelations(aggregateSynsets,predicateFamily)
        # Mabe combine with hypo ranks????
        # We generate relations using base, first:
        #pdb.set_trace()
        baseModel = BaseModel(subjectFamily.getBaseRanking()[0], predicateFamily.getBaseRanking()[0], objectFamily.getBaseRanking()[0])
        relationList = generateRelations(subjectFamily.getBaseHypoRanking(), relationRanks, objectFamily.getBaseHypoRanking())
        queryApproximates[relation]=[]
        for unrankedRelation in relationList:
            queryApproximates[relation].append(RankedRelation(baseModel.getModel(),  unrankedRelation, baseModel.rank(unrankedRelation)))
        #pdb.set_trace()
    return queryApproximates




def get_node_ids(path):
    cursor = get_cursors(path)
    ids = dict(cursor.execute('Select synset,id from synset_count'))
    cursor.close()
    return ids
def get_aggregate_ids(path):
    aggregate_curs = get_cursors(path)
    temp_aggregate_ids = aggregate_curs.execute('Select rel_id,subj_id,obj_id,id from aggregate_id').fetchall()
    aggregate_ids = {(item[0],item[1],item[2]):item[3] for item in temp_aggregate_ids}
    temp_aggregate_ids = None
    aggregate_curs.close()
    return aggregate_ids

def get_aggregate_image_ids(path):
    with open(path,'r') as id_file:
        aggregate_image_ids = json.loads(id_file.read())
    for entry in aggregate_image_ids:
        aggregate_image_ids[entry] = [int(item) for item in aggregate_image_ids[entry]]
    return aggregate_image_ids
    

def get_cursors(path):
    conn_obj = sqlite3.connect(path)
    return conn_obj.cursor()




def clauseJoin(matchClause,conditionClause,returnClause):
    return matchClause+' '+conditionClause+' '+returnClause
def synset_cleaned(neo4j_result):
    return [item.values()[0]['synset'].encode("utf-8") for item in neo4j_result]
def sessionRun(clause, driver):
    with driver.session() as session:
        result = session.run(clause)
    return result
def subject_relations_approximates(subjects,objects, driver):
    matchClause = 'match (s:ssagObject)-[:SUBJ]->(r:ssagRelation)-[:OBJ]->(o:ssagObject)'
    conditionClause = 'where s.synset in '+str(subjects) + ' and o.synset in '+str(objects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause), driver)
def object_relations_approximates(objects,subjects, driver):
    matchClause = 'match (s:osagObject)-[:SUBJ]->(r:osagRelation)-[:OBJ]->(o:osagObject)'
    conditionClause = 'where o.synset in '+str(objects) + ' and s.synset in '+str(subjects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause), driver)
def ssag_object_approximates(subjects,relations, driver):
    matchClause = 'match (n:ssagObject)-[:SUBJ]->(r:ssagRelation)-[:OBJ]->(o:ssagObject)'
    conditionClause = 'where n.synset in '+str(subjects) +'and r.synset in ' + str(relations)
    returnClause = 'return o'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause), driver)

def generateRelations(gsubject,grelation,gobject):
    #pdb.set_trace()
    return list(product(gsubject,grelation,gobject))
def extractRelations(query_file_name):
    query_file = open(query_file_name,'r')
    nouns = {}
    predicates = {}
    for line in query_file:
        line = line.strip().split(',')
        if line[1] == 'n':
            nouns[int(line[0])] = line[2]
        if line[1] == 'r':
            predicates[int(line[0])] = (line[2],int(line[3]), int(line[4]))
    query_file.close()
    relations = []
    for entry in predicates:
        relations.append((nouns[predicates[entry][1]],predicates[entry][0],nouns[predicates[entry][2]]))
    return relations
def unique_intersection(aggregate_relation_object,aggregate_relation_subject):
    aggregate_relations = aggregate_relation_subject+aggregate_relation_object
    aggregate_relations = set([item for item in aggregate_relations if (item in aggregate_relation_subject and item in aggregate_relation_object)])
    return aggregate_relations
def toSynset(synsetList):
    return [wn.synset(item) for item in synsetList]
def predicate_summary(predicateFamily):
    predicateCounts={}
    for item in predicateFamily.getFullRanking():
        predicateCounts[wn.synset(item)]= predicateFamily.getFamilySynsetCounts()[item] if item in predicateFamily.getFamilySynsetCounts() else predicateFamily.getSisterSynsetCounts()[item]
    predicateSum = float(sum([predicateCounts[item] for item in predicateCounts]))
    return predicateCounts,predicateSum
def rankRelations(aggregateSynsets,predicateFamily):
    predicateSynsets = toSynset(predicateFamily.getFullRanking())
    predicateCounts, predicateSum = predicate_summary(predicateFamily)
    rankingAverages=[]
    for item in aggregateSynsets:
        tSum = 0
        for mains in predicateSynsets:
            try:
                tSum += item.wup_similarity(mains) * (predicateCounts[mains]/predicateSum)
            except WordNetError:
                tSum += 0
            except TypeError:
                tSum += 0
        #tSum=sum(tSum)/len(predicateCounts)
        rankingAverages.append((str(item)[8:-2],tSum))
    rankingAverages = sorted(rankingAverages,key=lambda x:x[1],reverse=True)
    return [item[0] for item in rankingAverages if item[1] >= (2./3)*rankingAverages[0][1]]