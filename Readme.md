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

- `aggregate_image_ids.vgm`
- `image_urls.json`

### Database Requirements
The `databases` folder also requires the following non-text files:

- `aggregate.db`
- `objects.db`
- `relations.db`
- `GoogleNews-vectors-negative300.bin`
- `wn_embedding.h5`

### Software Requirements
A Neo4J server must be running with the aggregate graph databases already imported <-- TODO ADD DETAILS -->



## Execution
We will describe both example and UI,

### Example
`tester.py` performs a sample run of the Image Retriever. You may replace the query in the file with queries of your own from the `queries` folder. The file can also be modified to keep running queries. The first query of a session always takes the longest as the backend must setup a cache for graph search.

The setup takes ~3-4 minutes.

### UI
