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
    
    doc -- a JSON-LD document string
    
    Returns: string
    
    Usage:
    $ ./json_ld_to_ntriples.py ../test/json_ld_org_landing_page_example.json
    <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
    <http://example.org/people#john> <http://xmlns.com/foaf/0.1/name> "John Lennon" .
    '''
    ntriples = ""
    p = jlp.Processor()
    bnode_pattern = re.compile("^_\:\w+$")
    for t in p.triples(doc):
        if bnode_pattern.match(t["subj"]):
            ntriples += t["subj"].encode('utf-8')
        else:
            ntriples +=  "<" + t["subj"].encode('utf-8') + ">"
        ntriples +=  " <" + t["prop"].encode('utf-8') + ">"
        if bnode_pattern.match(t["obj"]):
            ntriples += ' %s' % t["obj"].encode('utf-8') + ' .\n'
        elif t["objtype"] == "resource":
            ntriples += " <" + t["obj"].encode('utf-8') + "> .\n"
        else:
            if t.has_key("lang"):
                ntriples += ' "%s"@%s' % (t["obj"].encode('utf-8'), t["lang"].encode('utf-8')) + ' .\n'
            elif t.has_key("datatype") and t["datatype"] != "http://www.w3.org/2001/XMLSchema#string":
                ntriples += ' "%s"^^<%s>' % (t["obj"].encode('utf-8'), t["datatype"].encode('utf-8')) + ' .\n'
            else:
                ntriples += ' "%s"' % t["obj"].encode('utf-8') + ' .\n'
    return ntriples
        
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    file = open(filename, 'r')
    doc = "".join(file.read().splitlines())
    print json_ld_to_ntriples(doc)
    

        

