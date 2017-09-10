from neo4j.v1 import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))


#spo - s: subject; v: verb/predicate/preposition; o: object

def exact-spo(e_subject, e_predicate, e_object):
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for record in tx.run("MATCH (a:Person)-[:LIKES]->(b) "
                                 "WHERE a.name = {name} "
                                 "RETURN b.name", name=name):
                print(record["b.name"])
                    
likes("Abhijit Suprem")