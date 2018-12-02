from nltk import Tree
import spacy

nlp = spacy.load('en')

query1 = 'man in a truck'
query2 = 'man in truck which has headlight'
query2 = 'man in truck with headlight'
query2 = 'man in truck, truck has headlight'
