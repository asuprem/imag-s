## Environment Installation

We are setting up a virtual environment. We will call it IMAG-S for **I**mage **M**atching with **A**pproximate **G**raph **S**earch

Packages to install:
- nltk
- sqlite3 <-- Maybe not?>
- neo4j-driver

## Setup

We need the `objects.db`, `relations.db`, `aggregate.db` databases into the databases folder. These will be used in `retrieval.py`

    $ python
    $ import nltk
    $ nltk_download('wordnet')

## Execution
Make sure the server is up, actually. Also make sure the VMG files are in the import folder, and import them using the CQLs.

    $ cypher-shell -u neo4j -p scientia < CQL\*.bat

    $ workon IMAGS
    $ python retrieval.py