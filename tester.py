import retriever
import pdb




if __name__ == "__main__":
    objectsdb_path   = 'databases/' + 'objects'   + '.db'
    relationsdb_path = 'databases/' + 'relations' + '.db'
    aggregatedb_path = 'databases/' + 'aggregate' + '.db'
    aggregate_path = 'aggregate_image_ids.vgm'
    IMAG = retriever.Retriever(objectsdb_path,relationsdb_path,aggregatedb_path,aggregate_path)

    uri = "bolt://localhost:7687"
    IMAG.set_driver(uri,'neo4j','scientia')



    query = ''
    with open('queries/query2.query', 'r') as q_file:
        q_file.readline()
        query = q_file.read()
    
    image_ids = IMAG.getQuery(query)
    pdb.set_trace()