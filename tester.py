from utils import retriever
import pdb
from utils import imageURL



if __name__ == "__main__":

    URL = imageURL.ImageURL('data/image_urls.json')
    pdb.set_trace()
    objectsdb_path   = 'databases/' + 'objects'   + '.db'
    relationsdb_path = 'databases/' + 'relations' + '.db'
    aggregatedb_path = 'databases/' + 'aggregate' + '.db'
    aggregate_path = 'databases/aggregate_image_ids.vgm'
    w2v_path = 'GoogleNews-vectors-negative300.bin'
    embedding_path = 'wn_embedding.h5'
    IMAG = retriever.Retriever(objectsdb_path,relationsdb_path,aggregatedb_path,aggregate_path, w2v_path, embedding_path)

    uri = "bolt://localhost:7687"
    IMAG.set_driver(uri,'neo4j','scientia')



    query = ''
    with open('queries/query2.query', 'r') as q_file:
        q_file.readline()
        query = q_file.read()
    #pdb.set_trace()
    image_ids = IMAG.getQuery(query)
    image_urls = URL.getURLs(image_ids)

    pdb.set_trace()