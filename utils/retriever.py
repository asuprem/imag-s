import sys, time, json, pdb, operator, sqlite3 h5utils
from nltk.corpus import wordnet as wn
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
        print("Setting up databases")
        self.object_ids = self.get_node_ids(objectdb)
        self.relation_ids = self.get_node_ids(relationdb)
        self.aggregate_ids = self.get_aggregate_ids(aggregatedb)
        print("Setting up explorers")
        self.aggregate_image_ids = self.get_aggregate_image_ids(aggregate_path)
        self.objectFamilies = SynsetExplorer(objectdb)
        self.relationFamilies = SynsetExplorer(relationdb)
        print("Setting up wordnet embeddings")
        self.embedding_wn = h5utils.load_dict_from_hdf5(embedding_path)
        print("Setting up w2v embeddings")
        self.w2v_model = KeyedVectors.load_word2vec_format(w2v_path, binary=True, unicode_errors='ignore')
        print("Finished setting up")

    #sets the driver
    def set_driver(self,uri,user,pw):
        self.driver = GraphDatabase.driver(uri, auth=(user, pw))
    
    def getApproximates(self,relations):
        #, objectFamilies, relationFamilies, driver):
        queryApproximates={}
        for relation in relations:
            #Get the explored synsets
            subjectFamily = self.objectFamilies.explore(relation[0])
            objectFamily = self.objectFamilies.explore(relation[2])
            predicateFamily = self.relationFamilies.explore(relation[1])
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
        for line in queryStr.splitlines():
            line = line.strip().split(',')
            if line[1] == 'n':
                nouns[int(line[0])] = line[2]
            if line[1] == 'r':
                predicates[int(line[0])] = (line[2],int(line[3]), int(line[4]))
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
