from neo4j.v1 import GraphDatabase
import pdb

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))


#spo - s: subject; v: verb/predicate/preposition; o: object

def exact_spo(e_subject, e_predicate, e_object):
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for record in tx.run(   "match (s:Object)-[:SUBJ]->(p:Relation)-[:OBJ]->(o:Object) "
                                    "where s.synset={e_subject} and "
                                    " p.synset={e_predicate} and "
                                    " o.synset={e_object} "
                                    "return s,p,o", 
                                    e_subject=e_subject, 
                                    e_object=e_object, 
                                    e_predicate=e_predicate):
                pdb.set_trace()
                #print(record["b.name"])
                    
    
def main():
    e_subject = input ("Query subject: ")
    e_predicate = input ("Query predicate: ")
    e_object = input ("Query object: ")

    exact_spo(e_subject, e_predicate, e_object)

if __name__ == "__main__":
    main()
