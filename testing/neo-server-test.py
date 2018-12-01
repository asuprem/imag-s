'''
This file was used to teest the Neo4j server stuff, likesample  returns and using the driver to make queries
'''
from neo4j.v1 import GraphDatabase
import pdb
import synset_explore

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
            for record in tx.run(   "match (s:MedObject)-[:SUBJ]->(p:MedRelation)-[:OBJ]->(o:MedObject) " + \
                                    match_construct + \
                                    "return s,p,o"):
                pdb.set_trace()
                #print(record["b.name"])
                    
def obj_count(obj_term):
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for record in tx.run("match (n:MedObject) where n.synset='" + obj_term + "' return count(n)"):
                return record['count(n)']



def main():
    #e_s_attr = raw_input ("Query subject attribute: ")
    
    #e_predicate = raw_input ("Query predicate: ")
    #e_object = raw_input ("Query object: ")
    #e_o_attr = raw_input ("Query object attribute: ")
    
    while 1:
        e_subject = raw_input ("Query subject: ")
        num_subj = obj_count(e_subject)
        print (e_subject +  ' : ' + str(num_subj) + '\n\n')
    
    #exact_spo(e_subject, e_predicate, e_object)

if __name__ == "__main__":
    main()



'''

match (s:Object)-[:SUBJ]->(r:Relation)-[:OBJ]->(o:Object)
where s.synset="leg.n.01"
return s,r,o

'''
