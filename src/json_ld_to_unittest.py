#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Oct 15, 2010

@author: ballen
'''

import json_ld_processor as jlp
from json_ld_to_ntriples import json_ld_to_ntriples

def json_ld_to_unittest(case, doc):
    '''
    Generates a unittest test case suitable to cut-and-paste into json_ld_processor.py,
    based on the deserialization of a JSON-LD document.
    
    Usage:
    $ ./json_ld_to_unittest.py nested_associative_array ../test/nested_associative_array.json 

    def test_nested_associative_array(self):
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode1", ...
        target_graph = [{'obj': u'<http://xmlns.com/foaf/0.1/Person>', 'subj': u'_:bn...
        self.json_ld_processing_test_case(doc, target_graph)
    '''
    p = jlp.Processor()
    print
    print "    def test_%s(self):" % case
    print "        '''"
    print "        JSON-LD:"
    print
    for line in doc.splitlines():
        print "        %s" % line
    print
    print "        N-Triples:"
    ntriples = json_ld_to_ntriples(doc)
    for line in ntriples.splitlines():
        print "        %s" % line
    print
    print "        '''"
    print "        p = jlp.Processor()"
    print "        doc = '%s'" % "".join(doc.splitlines())
    print "        generated_graph = [ t for t in p.triples(doc) ]"
    print "        target_graph = %s" % [ t for t in p.triples(doc) ]
    print "        self.assertTrue(graph_equal(target_graph, generated_graph))"
        
if __name__ == "__main__":
    import sys
    case = sys.argv[1]
    filename = sys.argv[2]
    file = open(filename, 'r')
    doc = "".join(file.read().splitlines())
    json_ld_to_unittest(case, doc)
