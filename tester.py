from utils import retriever
import pdb
from utils import imageURL
import warnings
warnings.simplefilter('error', RuntimeWarning)


if __name__ == "__main__":

    URL = imageURL.ImageURL('databases/image_urls.json')
    objectsdb_path   = 'databases/' + 'objects'   + '.db'
    relationsdb_path = 'databases/' + 'relations' + '.db'
    aggregatedb_path = 'databases/' + 'aggregate' + '.db'
    aggregate_path = 'databases/full_aggregate_image_ids.vgm'
    w2v_path = 'databases/GoogleNews-vectors-negative300.bin'
    embedding_path = 'databases/wn_embeddings.vgm'
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