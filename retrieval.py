import sys
import sqlite3
import operator
import time, json
from neo4j.v1 import GraphDatabase
import pdb
from synset_explorer import SynsetExplorer
import retrieval_utils
#import approximate_utils

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))

# RUN by python retrieval.py query1.query
def image_ids(approximate,object_ids,relation_ids,aggregate_ids,aggregate_image_ids):
    subj = object_ids[approximate[0]]
    pred = relation_ids[approximate[1]]
    obj = object_ids[approximate[2]]
    
    ids = aggregate_ids[(pred,subj,obj)] if (pred,subj,obj) in aggregate_ids else []
    return aggregate_image_ids[str(ids)] if ids else []
def main():

    conn_obj = sqlite3.connect('../ExtractedData/' + 'objects' + '.db')
    conn_rel = sqlite3.connect('../ExtractedData/' + 'relations' + '.db')
    conn_agg = sqlite3.connect('../ExtractedData/' + 'aggregate' + '.db')
    rel_curs = conn_rel.cursor()
    obj_curs = conn_obj.cursor()
    aggregate_curs = conn_agg.cursor()


    # these are global uniques
    object_ids = dict(obj_curs.execute('Select synset,id from synset_count'))
    relation_ids = dict(rel_curs.execute('Select synset,id from synset_count'))
    temp_aggregate_ids = aggregate_curs.execute('Select rel_id,subj_id,obj_id,id from aggregate_id').fetchall()
    aggregate_ids = {(item[0],item[1],item[2]):item[3] for item in temp_aggregate_ids}
    temp_aggregate_ids = None




    objectFamilies = SynsetExplorer('../ExtractedData/objects.db')
    relationFamilies = SynsetExplorer('../ExtractedData/relations.db')
    with open(sys.argv[1],'r') as id_file:
        aggregate_image_ids = json.loads(id_file.read())
    for entry in aggregate_image_ids:
        aggregate_image_ids[entry] = [int(item) for item in aggregate_image_ids[entry]]
    
    #query_file_name = sys.argv[1]
    while 1:
        query_file_name = raw_input("Query file:  ")
        query_file_name = 'queries/' + query_file_name + '.query'
        start=time.time()
        #Get the relations and nouns
        relations = retrieval_utils.extractRelations(query_file_name)
        #----------------------------------------------------------------------------#
        # USE the relation component approximates to generate relation approximates
        queryApproximates={}
        for relation in relations:
            #Get the explored synsets
            subjectFamily = objectFamilies.explore(relation[0])
            objectFamily = objectFamilies.explore(relation[2])
            predicateFamily = relationFamilies.explore(relation[1])
            #Get the cleaned up relations (i.e. without u'sdfdf' -> 'sdfdf')
            aggregate_relation_subject = retrieval_utils.synset_cleaned(retrieval_utils.subject_relations_approximates(subjectFamily.getFullRanking(),objectFamily.getFullRanking(), driver))
            aggregate_relation_object = retrieval_utils.synset_cleaned(retrieval_utils.object_relations_approximates(objectFamily.getFullRanking(),subjectFamily.getFullRanking(), driver))        
            #Get the unique relations and the predicate relations and convert to synset format (for lch similarity)
            aggregateSynsets = retrieval_utils.toSynset(retrieval_utils.unique_intersection(aggregate_relation_object,aggregate_relation_subject))
            #Get relationship ranks compared to the predicate family
            relationRanks = retrieval_utils.rankRelations(aggregateSynsets,predicateFamily)
            # Mabe combine with hypo ranks????
            # We generate relations using base, first:
            queryApproximates[relation] = retrieval_utils.generateRelations(subjectFamily.getFullRanking(), relationRanks, objectFamily.getFullRanking())

        print 'Finished getting relations in ' + str(time.time()-start)
        print '---------------------------------------------\n'
        #we have query approximates, and relations
        # we need to get images with the approximates in them.
        


        #pdb.set_trace()
        image_collection={}
        query_collection = {}
        for query in relations:
            image_collection[query]={}
            for approximate in queryApproximates[query]:
                #pdb.set_trace()        
                image_collection[query][approximate] = image_ids(approximate,object_ids,relation_ids,aggregate_ids,aggregate_image_ids)
                
                
                for ids in image_collection[query][approximate]:
                    if ids not in query_collection:
                        query_collection[ids] = {}
                    if query not in query_collection[ids]:
                        query_collection[ids][query]=[]
                    query_collection[ids][query].append(approximate)
                
            print 'Finished getting ' + str(query) + ' in '+ str(time.time()-start)
        #pdb.set_trace()
        
        out_counter = 0
        for entry in query_collection:
            if len(query_collection[entry])>1:
                print entry, query_collection[entry]
                out_counter+=1
                if out_counter > 5:
                    break
        print '---------------------------------------------\n'

if __name__ == "__main__":
    main()