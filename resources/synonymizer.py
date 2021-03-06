from gensim.models import Word2Vec
import re
from flask import jsonify, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.restful import Resource, reqparse
from flask.ext.restful.representations.json import output_json
import json
import ast # de-string incoming list
import itertools

print "Loading word2vec model"
#word2vec_model = "/media/data/GoogleNews-vectors-negative300.bin"
word2vec_model = "/app/GoogleNews-vectors-negative300.bin.gz"

prebuilt = Word2Vec.load_word2vec_format(word2vec_model, binary=True)
vocab_set = set(prebuilt.vocab.keys())
print "Done loading"

class SynonymizeAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', type=unicode, location='json')
        super(SynonymizeAPI, self).__init__()

    def get(self):
        return """ This service expects a POST in the form '{"text":["journalists"]}'.
It returns word2vec 'synonyms' of the term in the form '["REPORTER","INTERVIEWER"]'. 
                """

    def get_synonyms(self, word, match_n=5,threshold=0.7):
        word_upper = word.upper()
        word_title = word[0].capitalize() + word[1:].lower()
        word_lower = word.lower()

        word_combo = [word_upper,word_title,word_lower]

   #results_list = []
        results_dict={}
        for w in word_combo:
            try:
               results = prebuilt.most_similar(positive=[w], topn = match_n)
           #results_list.extend([i[0].upper() for i in results])
          # results_list.extend([i[0].upper() for i in results if i[1] >= threshold])
          # print [i[1] for i in results]
          #actual word will be the key and the value will be the similarity for the dictionary.
               for i in results:
                   if i[1]>=threshold:
                       results_dict[i[0]]=i[1]         
            except KeyError:
               pass
        return sorted(results_dict.keys(),key=results_dict.get,reverse=True)[0:match_n]
    
    def post(self):
        args = self.reqparse.parse_args()
        x = args['text']
        words = ast.literal_eval(x)
        print words
        print type(words)
        print len(words)
        if len(words) == 1:
            word = words[0]
            word = re.sub(" ", "_", word)
            syns = self.get_synonyms(word)
            syns = list(set(syns))
            word_order = [i.find(word.upper()) for i in syns]
            syns = [syn for (wo,syn) in sorted(zip(word_order, syns))][::-1]
        if len(words) == 2:
            word_list = [re.sub(" ", "_", w) for w in words]
            syns = []
            for n, w in enumerate(word_list):
                syns.append(self.get_synonyms(w, match_n = 5))
            t = [zip(x, syns[1]) for x in itertools.permutations(syns[0], len(syns[1]))]
            x = []
            for i in t:
                for j in i:
                    p = j[0] + "_" + j[1]
                    x.append(p)
            syns = list(set(x)) # get uniques
        if len(words) == 0 or len(words) > 2:
            print "Word length is 0 or greater than 2"
            syns = []
        
        return syns
