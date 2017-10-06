from neo4j.v1 import GraphDatabase
import pdb
import approximate_utils
'''
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))
'''
# RUN by python retrieval.py query1.query


def main():

    query_file = sys.argv[1]





    #exact_spo(e_subject, e_predicate, e_object)

if __name__ == "__main__":
    main()



'''

match (s:Object)-[:SUBJ]->(r:Relation)-[:OBJ]->(o:Object)
where s.synset="leg.n.01"
return s,r,o

'''
