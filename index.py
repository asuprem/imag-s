#!/usr/bin/env python
#basic imports
import os, json, sys
from json import dumps
#flask import
from flask import Flask, g, Response, request, render_template

#retriever imports + warning imports
from utils import retriever
import pdb, time, warnings
from utils import imageURL
warnings.simplefilter('error', RuntimeWarning)


#path loading
objectsdb_path   = 'databases/' + 'objects'   + '.db'
relationsdb_path = 'databases/' + 'relations' + '.db'
aggregatedb_path = 'databases/' + 'aggregate' + '.db'
aggregate_path = 'databases/full_aggregate_image_ids.vgm'
w2v_path = 'databases/GoogleNews-vectors-negative300.bin'
embedding_path = 'databases/wn_embeddings.vgm'
uri = "bolt://localhost:7687"

#setting up the retriever
IMAGS = retriever.Retriever(objectsdb_path,relationsdb_path,aggregatedb_path,aggregate_path, w2v_path, embedding_path)
IMAGS.set_driver(uri,'neo4j','scientia')
URL = imageURL.ImageURL('databases/image_urls.json')


# pics = os.path.join('static', 'pics')


app = Flask(__name__, static_url_path='/static/')
# app.config['UPLOAD_FOLDER'] = pics
# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = pics

@app.route("/")
def get_index():
	# full_filename = os.path.join(app.config['UPLOAD_FOLDER'],'graph.jpg')
	return app.send_static_file('index.html')


@app.route('/urls', methods=['GET','POST'])
def get_urls():
    try:
        print("connected")
        # q = request.args["q"]
        content = request.json
    except KeyError:
        print("error")
        return []
    else:
    	print("got input")
    	print(content)
    	with open('data.json', 'w') as outfile:
    		json.dump(content, outfile)
    	query = jsontoquery()
    	#print(query)

		#get query and push
        #pdb.set_trace()
        image_ids = IMAGS.getQuery(query)
        image_urls = URL.getURLs(image_ids)
        print image_urls[:20]
        #print 'completed query in %3.4f' % (time.time()-start)
        #pdb.set_trace()




    	# qjson = json.loads("place for pictures")
    	# print(qjson)
    	# return json.dumps({'success':True}), qjson, {'ContentType':'application/json'}
    	return json.dumps({'status':'OK', 'pass':image_urls[:15]});
		# return Response(dumps("YES"),
		#                 mimetype="application/json")

@app.route('/my-link/')
def my_link():
  print('I got clicked!')

  return 'Click.'


def jsontoquery():
	with open('data.json') as data_file:
		data = json.load(data_file)
	noun={}
	relation={}
	source=[]
	target=[]
	
	for i in range(len(data["nodes"])):
	    if data["nodes"][i]["class"]=="noun":
	        #ncount=ncount+1
	        noun[int(data["nodes"][i]["id"])]=data["nodes"][i]["title"]
	    if data["nodes"][i]["class"]=="rel":
	        #rcounter=rcounter+1
	        relation[int(data["nodes"][i]["id"])]=data["nodes"][i]["title"]

	for i in range(len(data["edges"])):
	    source.append(data["edges"][i]["source"])
	    target.append(data["edges"][i]["target"])

	#relation appears in both source and target, each relation only once in source and target respectively
	#relation only connected to two nouns
	
	for key in relation:
		countSR = 0
		countTR = 0
		for i in source:
		    if i==key:
		        countSR=countSR+1
		for i in target:
		    if i==key:
		        countTR=countTR+1
		if(countTR!=countSR or countTR!=1 or countSR!=1):
		    print("This query is not valid")
		    return []
		    # sys.exit()
		else:
		    print("Relation "+relation[key]+" is valid!")

	#no noun-to-noun connections
	#no relation to relation connections

	for i in range(len(data["edges"])):
	    if data["edges"][i]["source"] in noun.keys() and data["edges"][i]["target"] in noun.keys():
	        print("This query is not valid")
	        return []
	        # sys.exit()
	    if data["edges"][i]["source"] in relation.keys() and data["edges"][i]["target"] in relation.keys():
	        print("This query is not valid!")
	        return []
	        # sys.exit()

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

	nc={}
	ncount=0
	for key in noun:
		ncount=ncount+1
		nc[key]=ncount

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
	    query=query+str(rcounter)+",r,"+value+","+str(nc[sourceval])+","+str(nc[targetval])+"\n"
	    sourceval=0
	    targetval=0

	return query





if __name__ == '__main__':
    app.run(port=8080, debug=False)
