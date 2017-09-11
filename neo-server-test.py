from neo4j.v1 import GraphDatabase
import pdb

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))


#spo - s: subject; v: verb/predicate/preposition; o: object

def exact_spo(e_subject, e_predicate, e_object):
    clause = []
    if e_subject!='*':
        clause.append(('s.synset="'+e_subject+'" '))
    if e_predicate!='*':
        clause.append(('p.synset="'+e_predicate + '" '))
    if e_object!='*':
        clause.append(('o.synset="'+e_object + '" '))
    where  = 'where ' if len(clause)>=1 else ' '
    and_clause = ['and ' for item in clause][:-1]
    match_construct = where + clause[0]
    for idx in range(len(and_clause)):
        match_construct += and_clause[idx]+clause[idx+1]
    
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for record in tx.run(   "match (s:Object)-[:SUBJ]->(p:Relation)-[:OBJ]->(o:Object) " + \
                                    match_construct + \
                                    "return s,p,o"):
                pdb.set_trace()
                #print(record["b.name"])
                    
    
def main():
    e_s_attr = raw_input ("Query subject attribute: ")
    e_subject = raw_input ("Query subject: ")
    e_predicate = raw_input ("Query predicate: ")
    e_object = raw_input ("Query object: ")
    e_o_attr = raw_input ("Query object attribute: ")

    exact_spo(e_subject, e_predicate, e_object)

if __name__ == "__main__":
    main()



'''

match (s:Object)-[:SUBJ]->(r:Relation)-[:OBJ]->(o:Object)
where s.synset="leg.n.01"
return s,r,o

'''