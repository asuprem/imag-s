import pdb

def extractRelations(queryStr):
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
    pdb.set_trace()
    return relations

with open('../queries/query2.query', 'r') as q_file:
    q_file.readline()
    query = q_file.read()
    

extractRelations(query)