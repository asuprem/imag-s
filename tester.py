from utils import retriever
import pdb, time, warnings
from utils import imageURL
warnings.simplefilter('error', RuntimeWarning)


if __name__ == "__main__":

    objectsdb_path   = 'databases/' + 'objects'   + '.db'
    relationsdb_path = 'databases/' + 'relations' + '.db'
    aggregatedb_path = 'databases/' + 'aggregate' + '.db'
    aggregate_path = 'databases/full_aggregate_image_ids.vgm'
    w2v_path = 'databases/GoogleNews-vectors-negative300.bin'
    embedding_path = 'databases/wn_embeddings.vgm'
    uri = "bolt://localhost:7687"
    
    IMAGS = retriever.Retriever(objectsdb_path,relationsdb_path,aggregatedb_path,aggregate_path, w2v_path, embedding_path)
    IMAGS.set_driver(uri,'neo4j','scientia')
    URL = imageURL.ImageURL('databases/image_urls.json')


    query = ''
    while(1):
        query_file_name = raw_input("Query file:  ")
        start = time.time()
        with open('queries/'+query_file_name+'.query', 'r') as q_file:
            q_file.readline()
            query = q_file.read()
        #pdb.set_trace()
        image_ids = IMAGS.getQuery(query)
        image_urls = URL.getURLs(image_ids)
        print image_urls[:20]
        print 'completed query in %3.4f' % (time.time()-start)
        pdb.set_trace()