# IMAG-S: Image Matching with Approximate Graph Search

The IMAG-S platform allows one to perform fast approximate image retrieval ussing approximate graph search on scene graphs. We do not cover cache and database setup here. Instead, this repository only discusses setup and execution options for the IMAG-S platform. We assume Step 0 is completed.

**Step 0** refers to following the instructions in the neo-csv-gen repository's `Code Steps.md` file.

## Requirements

We cover package, file, database, and software requirements to set up and run the program.

### Package Requirements
All packages can be found in `requirements.txt`. A virtual environment is highly recommended. For the NLTK package, you eed to download the NLTK wordnet corpus.

#### NLTK Wordnet Corpus
Start python in the virtual environment with the NLTK package installed.

    $ import nltk
    $ nltk.download('wordnet')

### File Requirements
The top level directory requires a `databases` folder with the following files generated from Step 0.

- `full_aggregate_image_ids.vgm` - This is an inverted index of aggregate triplet ids mapped to image ids and objects within the image
- `image_urls.json` - This is a mapping of image ids to their URLs from the Visual Genome dataset
- `wn_embeddings.vgm`

### Database Requirements
The `databases` folder also requires the following non-text files:

- `aggregate.db`
- `objects.db`
- `relations.db`
- `GoogleNews-vectors-negative300.bin`

### Software Requirements
A Neo4J server must be running with the aggregate graph databases already imported <-- TODO ADD DETAILS -->

### Links
All files for the databases folder can be found [here](https://drive.google.com/open?id=1KIjqP7h7p3vIczy7-yDS0UuvL54vIqYz).

You still need to download the Google news vectors, though. You can find that [here](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM)

## Execution
We will describe both example and UI.

### Example
`tester.py` performs a sample run of the Image Retriever. You may replace the query in the file with queries of your own from the `queries` folder. The file can also be modified to keep running queries. The first query of a session always takes the longest as the backend must setup a cache for graph search.

The setup takes ~100s.

Execute `tester.py` using:

    $ python tester.py

When it prompts, provide a query file name from the queries folder. You just need the base name, without the extension:

    $ 

### UI
