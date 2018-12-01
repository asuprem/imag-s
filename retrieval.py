import sys
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
import sqlite3
import operator
import time
from neo4j.v1 import GraphDatabase
import pdb
from synset_explorer import SynsetExplorer
#from synset_explorer import Families
import retrieval_utils
#import approximate_utils

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))

# python retrieval.py ../ExtractedData/aggregate_image_ids.vgm

def image_ids(approximate,object_ids,relation_ids,aggregate_ids,aggregate_image_ids):
    subj = object_ids[approximate[0]]
    pred = relation_ids[approximate[1]]
    obj = object_ids[approximate[2]]
    
    ids = aggregate_ids[(pred,subj,obj)] if (pred,subj,obj) in aggregate_ids else []
    return aggregate_image_ids[str(ids)] if ids else []
def main():

    objectsdb_path   = 'databases/' + 'objects'   + '.db'
    relationsdb_path = 'databases/' + 'relations' + '.db'
    aggregatedb_path = 'databases/' + 'aggregate' + '.db'
    
    object_ids = retrieval_utils.get_node_ids(objectsdb_path)
    relation_ids = retrieval_utils.get_node_ids(relationsdb_path)
    aggregate_ids = retrieval_utils.get_aggregate_ids(aggregatedb_path)
    aggregate_image_ids = retrieval_utils.get_aggregate_image_ids(sys.argv[1])

    objectFamilies = SynsetExplorer(objectsdb_path)
    relationFamilies = SynsetExplorer(relationsdb_path)
    
    
    #query_file_name = sys.argv[1]
    while 1:
        query_file_name = raw_input("Query file:  ")
        query_file_name = 'queries/' + query_file_name + '.query'
        start=time.time()
        #Get the relations and nouns
        relations = retrieval_utils.extractRelations(query_file_name)
        #pdb.set_trace()
        # USE the relation component approximates to generate relation approximates
        queryApproximates = retrieval_utils.getApproximates(relations, objectFamilies, relationFamilies,driver)
        #pdb.set_trace()
        print 'Finished getting relations in ' + str(time.time()-start)
        print '---------------------------------------------\n'
        # we need to get images with the approximates in them.

        
        #pdb.set_trace()
        image_collection={}
        query_collection = {}
        for query in relations:
            image_collection[query]={}
            for approximate in queryApproximates[query]:
                #pdb.set_trace()        
                image_collection[query][approximate] = image_ids(approximate.getRelation(),object_ids,relation_ids,aggregate_ids,aggregate_image_ids)
                
                
                for ids in image_collection[query][approximate]:
                    if ids not in query_collection:
                        query_collection[ids] = {}
                    if query not in query_collection[ids]:
                        query_collection[ids][query]=[]
                    query_collection[ids][query].append(approximate)
                
            print 'Finished getting ' + str(query) + ' in '+ str(time.time()-start)
        
        #pdb.set_trace()
        out_counter = 0
        images_ranked={}
        for vgm_image_id in query_collection:

            query_list = [item for item in query_collection[vgm_image_id]]
            image_rank = 1
            for query in query_list:
                query_ranks = [item.getRank() for item in query_collection[vgm_image_id][query]]
                image_rank*=max(query_ranks)
            images_ranked[vgm_image_id] = image_rank
            '''
            if len(query_collection[entry])>1:
                
            '''
        ranked_images = [item[0] for item in sorted(images_ranked.items(), key=operator.itemgetter(1), reverse=True)]
        for item in ranked_images:
            #pdb.set_trace()
            print item, [(mod, [(subitem.getModel(),subitem.getRank()) for subitem in query_collection[item][mod]]) for mod in query_collection[item]]
            out_counter+=1
            if out_counter > 20:
                break
        print '---------------------------------------------\n'
        
if __name__ == "__main__":
    main()
