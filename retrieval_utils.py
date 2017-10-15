from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from itertools import product



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
        predicateCounts[wn.synset(item)]= predicateFamily.getFamilySynsetCounts()[item] if item in predicateFamily.getFamilySynsetCounts() else predicateFamily.getTopLevelSynsetCounts()[item]
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