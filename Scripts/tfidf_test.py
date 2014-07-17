#!/usr/bin/env python
# 
# Copyright (C) 2009 Niniane Wang.  All rights reserved.

__author__ = "Niniane Wang"
__email__ = "niniane at gmail dot com"

import math
import tfidf
import unittest
import nltk
import glob



DEFAULT_IDF_UNITTEST = 1.0

def get_exected_idf(num_docs_total, num_docs_term):
   return math.log(float(1 + num_docs_total) / (1 + num_docs_term))

class TfIdfTest(unittest.TestCase):


  def testKeywords(self):

    """Test retrieving keywords from a document, ordered by tf-idf."""
      #my_tfidf = tfidf.TfIdf(DEFAULT_IDF = 0.01)
      #allfiles = glob.glob("/Users/hijungshin/Dropbox/adobe_ctl/tfidf/khan_fluid/transcript*.txt")
        # for myfile in allfiles:
        #  my_tfidf.add_input_document(myfile)
        
    
      # my_tfidf.save_corpus_to_file("fluid_idf.txt", "fluid_stop.txt")
      #
      #keywords = my_tfidf.get_doc_keywords("/Users/hijungshin/Dropbox/adobe_ctl/tfidf/khan_fluid/transcript5.txt")
      #output_file = open("fluid_keywords5.txt", "w")
        #for keyword in keywords:
#  output_file.write(str(keyword) + "\n")

    guten_tfidf=tfidf.TfIdf(DEFAULT_IDF = 0.01)
    for fileid in nltk.corpus.gutenberg.fileids():
        guten_tfidf.add_input_document("/Users/hijungshin/nltk_data/corpora/gutenberg/"+fileid)
    
    guten_tfidf.save_corpus_to_file("guten_idf.txt", "guten_stop.txt")
    guten_keywords = guten_tfidf.get_doc_keywords("/Users/hijungshin/Dropbox/adobe_ctl/tfidf/khan_fluid/transcript.txt")
    output_file = open("fluid_gutenberg_keywords.txt", "w")
    for keyword in guten_keywords:
      output_file.write(str(keyword) + "\n")
 

def main():
  unittest.main()

if __name__ == '__main__':
  main()
