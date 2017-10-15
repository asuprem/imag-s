import sys
import operator
import time
from neo4j.v1 import GraphDatabase
import pdb
from synset_explorer import SynsetExplorer
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from itertools import product
#import approximate_utils

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))





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
def clauseJoin(matchClause,conditionClause,returnClause):
    return matchClause+' '+conditionClause+' '+returnClause
def synset_cleaned(neo4j_result):
    return [item.values()[0]['synset'].encode("utf-8") for item in neo4j_result]
def sessionRun(clause):
    with driver.session() as session:
        result = session.run(clause)
    return result
def subject_relations_approximates(subjects,objects):
    matchClause = 'match (s:ssagObject)-[:SUBJ]->(r:ssagRelation)-[:OBJ]->(o:ssagObject)'
    conditionClause = 'where s.synset in '+str(subjects) + ' and o.synset in '+str(objects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))
def object_relations_approximates(objects,subjects):
    matchClause = 'match (s:osagObject)-[:SUBJ]->(r:osagRelation)-[:OBJ]->(o:osagObject)'
    conditionClause = 'where o.synset in '+str(objects) + ' and s.synset in '+str(subjects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))


def oldsubject_relations_approximates(subjects):
    matchClause = 'match (n:aggregateObject)-[:SUBJ]->(r:aggregateRelation)'
    conditionClause = 'where n.synset in '+str(subjects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))
def oldobject_relations_approximates(objects):
    matchClause = 'match (r:aggregateRelation)-[:OBJ]->(o:aggregateObject)'
    conditionClause = 'where o.synset in '+str(objects)
    returnClause = 'return r'
    return sessionRun(clauseJoin(matchClause,conditionClause,returnClause))
def unique_intersection(aggregate_relation_object,aggregate_relation_subject):
    aggregate_relations = aggregate_relation_subject+aggregate_relation_object
    aggregate_relations = set([item for item in aggregate_relations if (item in aggregate_relation_subject and item in aggregate_relation_object)])
    return aggregate_relations
def main():

    objectFamilies = SynsetExplorer('../ExtractedData/objects.db')
    relationFamilies = SynsetExplorer('../ExtractedData/relations.db')
    #query_file_name = sys.argv[1]
    while 1:
        query_file_name = raw_input("Query file:  ")
        #Get the relations and nouns
        relations = extractRelations(query_file_name)
        #----------------------------------------------------------------------------#
        # USE the relation component approximates to generate relation approximates
        queryApproximates={}
        for relation in relations:
            #Get the explored synsets
            subjectFamily = objectFamilies.explore(relation[0])
            objectFamily = objectFamilies.explore(relation[2])
            predicateFamily = relationFamilies.explore(relation[1])
            #pdb.set_trace()
            start=time.time()
            #Get the cleaned up relations (i.e. without u'sdfdf' -> 'sdfdf')
            pdb.set_trace()
            aggregate_relation_subject = synset_cleaned(subject_relations_approximates(subjectFamily.getFullRanking(),objectFamily.getFullRanking()))
            aggregate_relation_object = synset_cleaned(object_relations_approximates(objectFamily.getFullRanking(),subjectFamily.getFullRanking()))
            #Get the unique relations and the predicate relations and convert to synset format (for lch similarity)
            #pdb.set_trace()
            '''
            aggregateSynsets = toSynset(unique_intersection(aggregate_relation_object,aggregate_relation_subject))
            #Get relationship ranks compared to the predicate family
            relationRanks = rankRelations(aggregateSynsets,predicateFamily)
            #pdb.set_trace()
            # Mabe combine with hypo ranks????
            # We generate relations using base, first:
            queryApproximates[relation] = generateRelations(subjectFamily.getFullRanking(), relationRanks, objectFamily.getFullRanking())

        print 'Finished getting relations in ' + str(time.time()-start)
        print '---------------------------------------------\n\n'
        #we have query approximates, and relations
        # we need to get images with the approximates in them.
        
        image_collection={}
        query_collection = {}
        for query in relations:
            image_collection[query]={}
            for approximate in queryApproximates[query]:
                image_collection[query][approximate] = image_ids(approximate)
                for ids in image_collection[query][approximate]:
                    if ids not in query_collection:
                        query_collection[ids] = {}
                    if query not in query_collection[ids]:
                        query_collection[ids][query]=[]
                    query_collection[ids][query].append(approximate)
            print 'Finished getting ' + str(query) + ' in '+ str(time.time()-start)
        
        for entry in query_collection:
            if len(query_collection[entry])>1:
                print entry, query_collection[entry]

    pdb.set_trace()
            '''



    
if __name__ == "__main__":
    main()
