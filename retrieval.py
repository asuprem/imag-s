from neo4j.v1 import GraphDatabase
import pdb
from synset_explorer import Synset_Explorer
#import approximate_utils

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))

# RUN by python retrieval.py query1.query

def clauseJoin(matchClause,conditionClause,returnClause):
    return matchClause+' '+conditionClause+' '+returnClause

def subject_relations_approximates(subjects):
    matchClause = 'match (n:aggregateObject)-[:SUBJ]->(r:aggregateRelation)'
    conditionClause = 'where s.synset in '+str(subjects)
    returnClause = 'return r'
    
    fullClause = clauseJoin(matchClause,conditionClause,returnClause)
    
    with driver.session() as session:
        with session.begin_transaction() as tx:
            result = tx.run(fullClause)
    pdb.set_trace()






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
        objectFamily = objects.explore(relations[1])
        pdb.set_trace()

        





    






if __name__ == "__main__":
    main()



'''

match (s:Object)-[:SUBJ]->(r:Relation)-[:OBJ]->(o:Object)
where s.synset="leg.n.01"
return s,r,o

'''
