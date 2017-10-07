import time
from neo4j.v1 import GraphDatabase
import pdb
from synset_explorer import Synset_Explorer
#import approximate_utils

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))

# RUN by python retrieval.py query1.query

def clauseJoin(matchClause,conditionClause,returnClause):
    return matchClause+' '+conditionClause+' '+returnClause

def sessionRun(clause):
    with driver.session() as session:
        result = session.run(clause)
    return result
def subject_relations_approximates(subjects):
    matchClause = 'match (n:aggregateObject)-[:SUBJ]->(r:aggregateRelation)'
    conditionClause = 'where n.synset in '+str(subjects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))
def ssag_object_approximates(subjects,relations):
    matchClause = 'match (n:ssagObject)-[:SUBJ]->(r:ssagRelation)-[:OBJ]->(o:ssagObject)'
    conditionClause = 'where n.synset in '+str(subjects) +'and r.synset in ' + str(relations)
    returnClause = 'return o'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))


def main():

    objects = Synset_Explorer('../ExtractedData/objects.db')
    relations = Synset_Explorer('../ExtractedData/relations.db')
    #query_file_name = sys.argv[1]
    query_file_name = 'queries/query2.query'
    query_file = open(query_file_name,'r')

    nouns = {}
    predicates = {}

    #Get the relations and nouns
    for line in query_file:
        line = line.strip().split(',')
        if line[1] == 'n':
            nouns[int(line[0])] = line[2]
        if line[1] == 'r':
            predicates[int(line[0])] = (line[2],int(line[3]), int(line[4]))
    
    relations = []
    for entry in predicates:
        relations.append((nouns[predicates[entry][1]],predicates[entry][0],nouns[predicates[entry][2]]))

    #----------------------------------------------------------------------------#
    # USE the relation component approximates to generate relation approximates
    queryApproximates=[]
    for relation in relations:
        subjectFamily = objects.explore(relation[0])
        objectFamily = objects.explore(relation[2])
        start=time.time()
        result = subject_relations_approximates(subjectFamily)
        aggregate_relation_subject = [item.values()[0]['synset'].encode("utf-8") for item in result]
        print 'Finished getting relations in ' + str(time.time()-start)
        result = ssag_object_approximates(subjectFamily,aggregate_relation_subject)
        ssag_objects = [item.values()[0]['synset'].encode("utf-8") for item in result]
        print 'Finished getting ssag Objects in ' + str(time.time()-start)



        pdb.set_trace()
        





    






if __name__ == "__main__":
    main()



'''

match (s:Object)-[:SUBJ]->(r:Relation)-[:OBJ]->(o:Object)
where s.synset="leg.n.01"
return s,r,o

'''
