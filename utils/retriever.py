import sys, time, json, pdb, operator, sqlite3, h5utils
from nltk.corpus import wordnet as wn
import numpy as np
from nltk.corpus.reader.wordnet import WordNetError
from itertools import product
from neo4j.v1 import GraphDatabase
from synset_explorer import SynsetExplorer
from rankedRelation import RankedRelation
from baseModel import BaseModel
from gensim.models import KeyedVectors
from gensim.utils import tokenize

#from synset_explorer import Families
#import retrieval_utils

#import approximate_utils

#uri = "bolt://localhost:7687"
#driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))

class Retriever:

    def __init__(self, objectdb, relationdb, aggregatedb,aggregate_path, w2v_path, embedding_path):
        self.driver = None

        #objectsdb_path   = 'databases/' + 'objects'   + '.db'
        #relationsdb_path = 'databases/' + 'relations' + '.db'
        #aggregatedb_path = 'databases/' + 'aggregate' + '.db'
        start = time.time()
        print("Setting up databases at %3.4f" % (time.time()-start))
        self.object_ids = self.get_node_ids(objectdb)
        self.relation_ids = self.get_node_ids(relationdb)
        self.aggregate_ids = self.get_aggregate_ids(aggregatedb)
        print("Setting up explorers at %3.4f" % (time.time()-start))
        self.aggregate_image_ids = self.get_aggregate_image_ids(aggregate_path)
        self.objectFamilies = SynsetExplorer(objectdb)
        self.relationFamilies = SynsetExplorer(relationdb)
        print("Setting up wordnet embeddings at %3.4f" % (time.time()-start))
        self.embedding_wn = h5utils.load_dict_from_hdf5(embedding_path)
        print("Setting up w2v embeddings at %3.4f" % (time.time()-start))
        self.w2v_model = KeyedVectors.load_word2vec_format(w2v_path, binary=True, unicode_errors='ignore')
        print("Finished setting up at %3.4f" % (time.time()-start))

    #sets the driver
    def set_driver(self,uri,user,pw):
        self.driver = GraphDatabase.driver(uri, auth=(user, pw))
    
    def getApproximates(self,relations):
        #, objectFamilies, relationFamilies, driver):
        queryApproximates={}
        for relation in relations:
            #Get the explored synsets
            subjectFamily = self.objectFamilies.explore(relation[0][0])
            objectFamily = self.objectFamilies.explore(relation[2][0])
            predicateFamily = self.relationFamilies.explore(relation[1][0])
            #Get the cleaned up relations (i.e. without u'sdfdf' -> 'sdfdf')
            #pdb.set_trace()
            aggregate_relation_subject = self.synset_cleaned(self.subject_relations_approximates(subjectFamily.getBaseHypoRanking(),objectFamily.getBaseHypoRanking()))
            aggregate_relation_object = self.synset_cleaned(self.object_relations_approximates(objectFamily.getBaseHypoRanking(),subjectFamily.getBaseHypoRanking()))        
            #Get the unique relations and the predicate relations and convert to synset format (for lch (or wup<--this is used) similarity) 
            #(this gets unique predicates from osag and ssag)
            aggregateSynsets = self.toSynset(self.unique_intersection(aggregate_relation_object,aggregate_relation_subject))
            #Get relationship ranks compared to the predicate family (i.e. top predicates????)
            relationRanks = self.rankRelations(aggregateSynsets,predicateFamily)
            # Mabe combine with hypo ranks????
            # We generate relations using base, first:
            baseModel = BaseModel(subjectFamily, predicateFamily, objectFamily)
            #generate relations creates the approximates using top ranked relations and subjFamily and objFamily hypos
            relationList = self.generateRelations(subjectFamily.getBaseHypoRanking(), relationRanks, objectFamily.getBaseHypoRanking())
            queryApproximates[relation]=[]
            #for each relation in relationList (which was gen by taking families of obj and subj, and top2/3 families of rel)
            for unrankedRelation in relationList:
                queryApproximates[relation].append(RankedRelation(baseModel.getModel(),  unrankedRelation, baseModel.rank(unrankedRelation, self.embedding_wn, self.w2v_model)))
            #pdb.set_trace()
        return queryApproximates

    def synset_cleaned(self,neo4j_result):
        return [item.values()[0]['synset'].encode("utf-8") for item in neo4j_result]

    def subject_relations_approximates(self,subjects,objects):
        matchClause = 'match (s:ssagObject)-[:SUBJ]->(r:ssagRelation)-[:OBJ]->(o:ssagObject)'
        conditionClause = 'where s.synset in '+str(subjects) + ' and o.synset in '+str(objects)
        returnClause = 'return r'
        return self.sessionRun(self.clauseJoin(matchClause,conditionClause,returnClause))
    def object_relations_approximates(self,objects,subjects):
        matchClause = 'match (s:osagObject)-[:SUBJ]->(r:osagRelation)-[:OBJ]->(o:osagObject)'
        conditionClause = 'where o.synset in '+str(objects) + ' and s.synset in '+str(subjects)
        returnClause = 'return r'
        return self.sessionRun(self.clauseJoin(matchClause,conditionClause,returnClause))
    def generateRelations(self,gsubject,grelation,gobject):
        return list(product(gsubject,grelation,gobject))

    def toSynset(self,synsetList):
        return [wn.synset(item) for item in synsetList]
    def unique_intersection(self,aggregate_relation_object,aggregate_relation_subject):
        aggregate_relations = aggregate_relation_subject+aggregate_relation_object
        aggregate_relations = set([item for item in aggregate_relations if (item in aggregate_relation_subject and item in aggregate_relation_object)])
        return aggregate_relations
    def clauseJoin(self,matchClause,conditionClause,returnClause):
        return matchClause+' '+conditionClause+' '+returnClause
    def sessionRun(self,clause):
        with self.driver.session() as session:
            result = session.run(clause)
        return result
    def extractRelations(self,queryStr):
        nouns = {}
        predicates = {}
        #add id_counter to keep track of collapse
        id_counter = 0
        for line in queryStr.splitlines():
            line = line.strip().split(',')
            if line[1] == 'n':
                nouns[int(line[0])] = (line[2],id_counter)
            if line[1] == 'r':
                predicates[int(line[0])] = ((line[2], id_counter),int(line[3]), int(line[4]))
            id_counter+=1
        relations = []
        for entry in predicates:
            relations.append((nouns[predicates[entry][1]],predicates[entry][0],nouns[predicates[entry][2]]))
        return relations


    def rankRelations(self,aggregateSynsets,predicateFamily):
        predicateSynsets = self.toSynset(predicateFamily.getFullRanking())
        predicateCounts, predicateSum = self.predicate_summary(predicateFamily)
        rankingAverages=[]
        #for each item in intersection of ssag and osag relations (i.e. the predicateApproximates)
        for item in aggregateSynsets:
            tSum = 0
            for mains in predicateSynsets:
                try:
                    #TODO update ranking function
                    #similarity between approximate and query relation sisters, weighted by count of sisters
                    #pdb.set_trace()
                    #synset to synset distance
                    tSum += item.wup_similarity(mains) * (predicateCounts[mains]/predicateSum)
                except WordNetError:
                    tSum += 0
                except TypeError:
                    tSum += 0
            #tSum=sum(tSum)/len(predicateCounts)
            rankingAverages.append((str(item)[8:-2],tSum))
        rankingAverages = sorted(rankingAverages,key=lambda x:x[1],reverse=True)
        #keep top 2/3 of image match
        return [item[0] for item in rankingAverages if item[1] >= (2./3)*rankingAverages[0][1]]
    def predicate_summary(self,predicateFamily):
        predicateCounts={}
        for item in predicateFamily.getFullRanking():
            predicateCounts[wn.synset(item)]= predicateFamily.getFamilySynsetCounts()[item] if item in predicateFamily.getFamilySynsetCounts() else predicateFamily.getSisterSynsetCounts()[item]
        #for normalization (i think) get predicate sum
        predicateSum = float(sum([predicateCounts[item] for item in predicateCounts]))
        return predicateCounts,predicateSum

    #unique triplet to image reverse matching for caching purposes
    def image_ids(self,approximate):
        subj = self.object_ids[approximate[0]]
        pred = self.relation_ids[approximate[1]]
        obj = self.object_ids[approximate[2]]
        
        ids = self.aggregate_ids[(pred,subj,obj)] if (pred,subj,obj) in self.aggregate_ids else []
        return self.aggregate_image_ids[str(ids)] if ids else []

    def get_node_ids(self,path):
        cursor = self.get_cursors(path)
        ids = dict(cursor.execute('Select synset,id from synset_count'))
        cursor.close()
        return ids
    def get_aggregate_ids(self,path):
        aggregate_curs = self.get_cursors(path)
        temp_aggregate_ids = aggregate_curs.execute('Select rel_id,subj_id,obj_id,id from aggregate_id').fetchall()
        aggregate_ids = {(item[0],item[1],item[2]):item[3] for item in temp_aggregate_ids}
        temp_aggregate_ids = None
        aggregate_curs.close()
        return aggregate_ids

    def get_cursors(self,path):
        conn_obj = sqlite3.connect(path)
        return conn_obj.cursor()

    def get_aggregate_image_ids(self,path):
        with open(path,'r') as id_file:
            aggregate_image_ids = json.loads(id_file.read())
        for entry in aggregate_image_ids:
            aggregate_image_ids[entry] = [int(item) for item in aggregate_image_ids[entry]]
        return aggregate_image_ids

    #This gets the actual query
    def getQuery(self,queryStr):

        #This extracts relations from the query String
        relations = self.extractRelations(queryStr)

        #NEW NEW added top level query
        # relations <-- [(('man', 0), ('in', 3), ('truck', 1)), (('truck', 1), ('has', 4), ('light', 2))]
        topLevelQueries = {relation:TopLevelQuery(relation) for relation in relations}
        for query in topLevelQueries:
            topLevelQueries[query].setEmbeddings(self.w2v_model)
        
        #This gets cooccurence to extarct comapping so we can get top level queries in their structure by separating independent subgraphs
        #node_id_cooccurence stores this info: for each node in a simplified triplet, where else does it occur.
        # so for man-in-truck and truck-has-light, truck is same. So we store this info - that truck node exists in relation 1 as object and relation 2 as subject
        query_ids,query_ids_inverted,node_ids_cooccurence = self.top_level_setup(relations)
        # query_ids <-- 0: (('man', 0), ('in', 3), ('truck', 1)), 1: (('truck', 1), ('has', 4), ('light', 2))}
        # query_ids_inverted <-- {(('man', 0), ('in', 3), ('truck', 1)): 0, (('truck', 1), ('has', 4), ('light', 2)): 1}
        # node_ids_coccurence <-- {0: [(0, 0)], 1: [(0, 2), (1, 0)], 2: [(1, 2)]}
        
        #query comapping is a simplification of node_ids_cooccurence, i.e. in which top level queries (without position information) does a node exist in
        # comapping <-- {0: [0], 1: [0, 1], 2: [1], 3: [0], 4: [1]}
        query_comappings = self.comap(relations,query_ids_inverted)
        #the following creates a separate top level query id that maps subqueries to top level quries
        #{0: 0, 1: 0}
        top_level_queries = self.get_top_level_queries(query_comappings)
        #this gets top plevel queries and nodes
        #inverted tlqs stores the canonical triplets that exist in a top levell query
        #inverted tlns stores the nodes that exist in a toplevel query
        #(Pdb) inverted_tlqs
        #{0: [0, 1]}
        #(Pdb) inverted_tlns
        #{0: set([0, 1, 2, 3, 4])}
        inverted_tlqs,inverted_tlns = self.query_inverted_indices(top_level_queries,topLevelQueries,query_ids)
        

        # USE the relation component approximates to generate relation approximates
        queryApproximates = self.getApproximates(relations)
        #print 'Finished getting relations in ' + str(time.time()-start)
        #print '---------------------------------------------\n'
        

        # we need to get images with the approximates in them.
        image_collection={}
        query_collection = {}
        #this is for each top level query
        for query in relations:
            #images that match this query
            image_collection[query]={}
            #For each approximate for this query
            for approximate in queryApproximates[query]:
                #get image ID associated with this approximate (from image_ids database)
                image_collection[query][approximate] = self.image_ids(approximate.getRelation())
                
                #inverted index of (Image-id,query) to approximate, i.e.
                # for each image
                    # store the queries. For each query
                        # store the approximates
                for ids in image_collection[query][approximate]:
                    pdb.set_trace()
                    if ids not in query_collection:
                        query_collection[ids] = {}
                    if query not in query_collection[ids]:
                        query_collection[ids][query]=[]
                    query_collection[ids][query].append(approximate)
            #print 'Finished getting ' + str(query) + ' in '+ str(time.time()-start)

        #Now we rank the image
        out_counter = 0
        images_ranked={}
        for vgm_image_id in query_collection:

            query_list = [item for item in query_collection[vgm_image_id]]
            image_rank = 1
            for query in query_list:
                #item is what????? (item is RankedRelation) TODO
                query_ranks = [item.getRank() for item in query_collection[vgm_image_id][query]]
                #here the ranks are multiplied <-- need to modify ranker in baseModel to use cos_sim
                #need to update this to sum? or keep multiply?? (no, sum and normalize) TODO
                image_rank*=min(query_ranks)
            images_ranked[vgm_image_id] = image_rank

        #sorted in descending order i.e. largest to smallest --> need to modify to sort from smallest to largest
        ranked_images = [item[0] for item in sorted(images_ranked.items(), key=operator.itemgetter(1))]
        return ranked_images
        #return list of URLs
    #This sets up coocurence matrix so same nodes are identified as such
    def top_level_setup(self,relations):
        query_ids = {}
        query_ids_inverted={}
        node_ids_cooccurence={}
        for idx,relation in enumerate(relations):
            query_ids[idx] = relation
            query_ids_inverted[relation] = idx
            for node_ in [0,2]:
                if relation[node_][1] not in node_ids_cooccurence:
                    node_ids_cooccurence[relation[node_][1]] = []
                node_ids_cooccurence[relation[node_][1]].append((idx,node_))
                #^ Format: node_id: [(parent_query_id, parent_query_location)...]
                # parent_query_location: 0-> subject; 2->object
        return query_ids,query_ids_inverted,node_ids_cooccurence
    def comap(self,relations, query_ids_inverted):
        query_comappings={}
        for relation in relations:
            for node in relation:
                if node[1] not in query_comappings:
                    query_comappings[node[1]] = [query_ids_inverted[relation]]
                else:
                    query_comappings[node[1]].append(query_ids_inverted[relation])
        return query_comappings
    def get_top_level_queries(self,query_comappings):
        top_level_queries = {}
        total_queries = 0
        for entry in query_comappings:
            if query_comappings[entry][0] not in top_level_queries:
                top_level_queries[query_comappings[entry][0]] = total_queries
                total_queries+=1
            current_group = top_level_queries[query_comappings[entry][0]]
            for query_idx in query_comappings[entry][1:]:
                top_level_queries[query_idx] = current_group
        return top_level_queries
    def query_inverted_indices(self,top_level_queries,topLevelQueries,query_ids):
        inverted_tlqs={}
        #inverted top level nodes
        inverted_tlns={}
        for entry in top_level_queries:
            if top_level_queries[entry] not in inverted_tlqs:
                inverted_tlqs[top_level_queries[entry]] = []
                inverted_tlns[top_level_queries[entry]] = []
            inverted_tlns[top_level_queries[entry]]+=list(topLevelQueries[query_ids[entry]].baseNodeIds)
            inverted_tlqs[top_level_queries[entry]].append(entry)
        inverted_tlns = {item:set(inverted_tlns[item]) for item in inverted_tlns}
        return inverted_tlqs,inverted_tlns
class TopLevelQuery:
    def __init__(self,query):
        #query: (('man', 1), ('in', 6), ('truck', 2))
        self.query = query
        self.baseQuery = tuple([item[0] for item in self.query])
        self.baseNodeIds = tuple([item[1] for item in self.query])
        self.subject_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        self.object_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        self.relation_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
    def setEmbeddings(self,embeddings=None):
        if self.baseQuery[0] in embeddings:
            self.subject_embedding = embeddings[self.baseQuery[0]].reshape(1,-1)
        else:
            self.subject_embedding = np.ones(300).reshape(1,-1)
        if self.baseQuery[1] in embeddings:
            self.relation_embedding = embeddings[self.baseQuery[1]].reshape(1,-1)
        else:
            self.relation_embedding = np.ones(300).reshape(1,-1)
        if self.baseQuery[2] in embeddings:
            self.object_embedding = embeddings[self.baseQuery[2]].reshape(1,-1)
        else:
            self.object_embedding = np.ones(300).reshape(1,-1)

        #self.subject_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        #self.object_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
        #self.relation_embedding = (2*np.random.rand(300)-1).reshape(1,-1)
    def getSubjectEmbedding(self):
        return self.subject_embedding
    def getObjectEmbedding(self):
        return self.object_embedding
    def getRelationEmbedding(self):
        return self.relation_embedding
