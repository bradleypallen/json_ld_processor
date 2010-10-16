#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Oct 15, 2010

@author: ballen
'''

import re, json_ld_processor as jlp

def json_ld_to_ntriples(doc):
    '''
    Serializes a set of triples into N-Triples format, based on the
    deserialization of a JSON-LD document.
    
    Usage:
    $ ./json_ld_to_ntriples.py ../test/json_ld_org_landing_page_example.json
    <http://example.org/people#john>
       <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
         <http://xmlns.com/foaf/0.1/Person> .
    <http://example.org/people#john>
       <http://xmlns.com/foaf/0.1/name>
        "John Lennon" .
    '''
    p = jlp.Processor()
    for t in p.triples(doc):
        print t["subj"].encode('utf-8')
        print "  ", t["prop"].encode('utf-8')
        if re.match("^_:.+$", t['obj']) or re.match("^<.+>$", t['obj']):
            print "    ", t["obj"].encode('utf-8'), '.'
        else:
            print '    "%s"' % t["obj"].encode('utf-8'), '.'
        
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    file = open(filename, 'r')
    doc = "".join(file.read().splitlines())
    json_ld_to_ntriples(doc)
    

        

