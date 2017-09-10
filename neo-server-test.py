from neo4j.v1 import GraphDatabase
import pdb

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))


#spo - s: subject; v: verb/predicate/preposition; o: object

def exact-spo(e_subject, e_predicate, e_object):
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for record in tx.run(   "match (s:Object)-[:SUBJ]->(p:Relation)-[:OBJ]->(o:Object) "
                                    "where s.synset={e_subject} "
                                    "where p.synset={e_predicate} "
                                    "where o.synset={e_object} "
                                    "return s,p,o", 
                                    e_subject=e_subject, 
                                    e_object=e_object, 
                                    e_predicate=e_predicate)
                pdb.set_trace()
                #print(record["b.name"])
                    
if __name__ == "__main__":
    exact-spo('leg.n.01', 'under.r.01', 'counter.n.01')



