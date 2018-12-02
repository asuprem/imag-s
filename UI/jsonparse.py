import json
from pprint import pprint
import sys

with open('data.json') as data_file:
    data = json.load(data_file)
noun={}
relation={}
source=[]
target=[]

for i in range(len(data["nodes"])):
    if data["nodes"][i]["class"]=="noun":
        #ncounter=ncounter+1
        noun[int(data["nodes"][i]["id"])]=data["nodes"][i]["title"]
    if data["nodes"][i]["class"]=="rel":
        #rcounter=rcounter+1
        relation[int(data["nodes"][i]["id"])]=data["nodes"][i]["title"]

for i in range(len(data["edges"])):
    source.append(data["edges"][i]["source"])
    target.append(data["edges"][i]["target"])

#relation appears in both source and target, each relation only once in source and target respectively
#relation only connected to two nouns
countSR=0
countTR=0
for key in relation:
    for i in source:
        if i==key:
            countSR=countSR+1
    for i in target:
        if i==key:
            countTR=countTR+1
    if(countTR!=countSR and countTR+countTR!=2):
        print("This query is not valid")
        sys.exit()
    else:
        print("Relation "+relation[key]+" is valid!")

#no noun-to-noun connections
#no relation to relation connections

for i in range(len(data["edges"])):
    if data["edges"][i]["source"] in noun.keys() and data["edges"][i]["target"] in noun.keys():
        print("This query is not valid")
    if data["edges"][i]["source"] in relation.keys() and data["edges"][i]["target"] in relation.keys():
        print("This query is not valid!")

flagnoun=0
keystopop=[]
for key in noun:
    for i in range(len(data["edges"])):
        if key==data["edges"][i]["source"] or key==data["edges"][i]["target"]:
            flagnoun=1
    if flagnoun!=1:
        keystopop.append(key)
    flagnoun=0

for i in keystopop:
    noun.pop(i)

ncounter=0
rcounter=0
#create final query
query=""
for key,value in noun.items():
    ncounter=ncounter+1
    query=query+str(ncounter)+",n,"+value+"\n"

sourceval=0
targetval=0
for key,value in relation.items():
    for i in range(len(data["edges"])):
        if data["edges"][i]["source"]==key:
            targetval=data["edges"][i]["target"]
    for i in range(len(data["edges"])):
        if data["edges"][i]["target"]==key:
            sourceval=data["edges"][i]["source"]
    rcounter=rcounter+1
    query=query+str(rcounter)+",r,"+value+","+str(sourceval)+","+str(targetval)+","+"\n"
    sourceval=0
    targetval=0

print(query)
