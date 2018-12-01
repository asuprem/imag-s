'''
This file is mostly a placeholder that was used to store some sample Cypher Queries.

'''
from neo4j.v1 import GraphDatabase
import pdb
import syset_explore

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "scientia"))


def main():

using periodic commit 500
load csv from "file:///objects-small.vgm" as line
create (a:Object {id:toInteger(line[0]), synset:line[1], name:line[2], img:toInteger(line[3])})

create constraint on (o:Object) assert o.id is unique

using periodic commit 500
load csv from "file:///attributes-small.vgm" as line
match (o:Object {id:toInteger(line[0])})
create (a:Attribute {name:line[1]})-[:ATTR]->(o)


using periodic commit 500
load csv from "file:///relations-small.vgm" as line
match (s:Object {id:toInteger(line[1])}), (o:Object {id:toInteger(line[2])})
create (s)-[:SUBJ]->(r:Relation {id:toInteger(line[0]), synset:line[3], name:line[4], img:toInteger(line[5])})-[:OBJ]->(o)


create constraint on (o:Relation) assert o.id is unique

create index on :Relation(synset)
create index on :Object(synset)


if __name__ == "__main__":
    main()
