# json_ld_processor: A document-based JSON-LD processor in Python

json_ld_processor is an implementation of a document-based (i.e., non-streaming) JSON-LD processor in Python.
    
[JSON-LD](http://json-ld.org) is a JSON representation format for Linked Data. A public working draft of a potential specification of 
JSON-LD is available at [http://json-ld.org/spec/latest/](http://json-ld.org/spec/latest/).
        
json_ld_processor is an experimental implementation, written to support work in understanding and helping to 
refine the JSON-LD draft specification. Therefore, one should expect rough but not complete compliance with 
the latest draft.
    
In fact, one should expect numerous bugs, inefficiencies, and gross misunderstandings of key concepts in 
the specification.
    
That being said, the processor, run from the command line, executes a test suite that shows 
correct behavior over a number of test cases taken from the draft specification and other communications 
about JSON-LD.
    
## Credits
Thanks to Manu Sporny and Mark Birbeck for drafting the JSON-LD specification.

# Requirements
Python 2.5 or above.

# Installation
$ git clone git@github.com:bradleypallen/json_ld_processor.git

# Modules

## json_ld_processor.py    
    class Processor(__builtin__.object)
     |  Defines a class for a JSON-LD processor, as specified in http://json-ld.org/spec/latest/.
     |  
     |  Methods defined here:
     |  
     |  __init__(self, context=None)
     |      Creates a JSON-LD Processor.
     |      
     |      Keyword arguments:
     |      context -- a Python dictionary providing the specification of a default context for the processor. 
     |      
     |      If context is None, the default context is equivalent to the following JSON-LD context:
     |      
     |      { 
     |        "#": {
     |               "__vocab__": "http://example.org/default-vocab#",
     |               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
     |               "xsd": "http://www.w3.org/2001/XMLSchema#",
     |               "dc": "http://purl.org/dc/terms/",
     |               "skos": "http://www.w3.org/2004/02/skos/core#",
     |               "foaf": "http://xmlns.com/foaf/0.1/",
     |               "sioc": "http://rdfs.org/sioc/ns#",
     |               "cc": "http://creativecommons.org/ns#",
     |               "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
     |               "vcard": "http://www.w3.org/2006/vcard/ns#",
     |               "cal": "http://www.w3.org/2002/12/cal/ical#",
     |               "doap": "http://usefulinc.com/ns/doap#",
     |               "Person": "http://xmlns.com/foaf/0.1/Person",
     |               "name": "http://xmlns.com/foaf/0.1/name",
     |               "homepage": "http://xmlns.com/foaf/0.1/homepage"
     |              }
     |      }
     |      
     |      Returns: an instance of json_ld_processor.Processor.
     |  
     |  triples(self, doc)
     |      An iterator that yields triples by deserializing a JSON_LD document.
     |      
     |      Arguments:
     |      doc -- a str instance containing a JSON_LD document.
     |      
     |      Returns: an iterator.
     |      
     |      Each triple is a Python dictionary with keys "subj", "prop" and "obj", each
     |      with values of the triple's subject, property and object, respectively.
     |      
     |      For example, the JSON-LD document
     |      
     |      {
     |        "#": {"foaf": "http://xmlns.com/foaf/0.1/"},
     |        "@": "<http://example.org/people#john>",
     |        "a": "foaf:Person",
     |        "foaf:name" : "John Lennon"
     |      }
     |      
     |      yields the following triples
     |      
     |      {
     |          'objtype': 'resource', 
     |          'subj': u'http://example.org/people#john', 
     |          'obj': u'http://xmlns.com/foaf/0.1/Person', 
     |          'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
     |      }, 
     |      {
     |          'objtype': 'literal', 
     |          'datatype': 'http://www.w3.org/2001/XMLSchema#string', 
     |          'obj': u'John Lennon', 
     |          'subj': u'http://example.org/people#john', 
     |          'prop': u'http://xmlns.com/foaf/0.1/name'
     |      }
     |      
     |      which can be serialized as follows in N-Triples format
     |      
     |      <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
     |      <http://example.org/people#john> <http://xmlns.com/foaf/0.1/name> "John Lennon" .
     |  
     
## json_ld_to_ntriples.py
    json_ld_to_ntriples(doc)
        Serializes a set of triples into N-Triples format, based on the
        deserialization of a JSON-LD document.
        
        Usage:
        $ ./json_ld_to_ntriples.py ../test/json_ld_org_landing_page_example.json
        <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#john> <http://xmlns.com/foaf/0.1/name> "John Lennon" .

## json_ld_test_suite.py
    class TestProcessor(unittest.TestCase)
     |  Defines a unittest test processor for automated unit testing of the JSON-LD processor.
     |  Tests are largely drawn from examples in the specification at http://json-ld.org/spec/latest/,
     |  but also include some based on individual and group conversations.
     |  
     |  Each test case simply takes a JSON-LD document, deserializes it using triples(),
     |  and asserts that the generated list of triples is the same as a target list of triples.
     |  
     |  Usage:    
     |  $ ./json_ld_test_suite.py 
     |  ......................
     |  ----------------------------------------------------------------------
     |  Ran 22 tests in 0.015s
     |  
     |  OK

# Test cases
All of the test cases in the test suite for json_ld_processor.py are provided as stand-alone files
in the /test directory.

# License
The MIT License

Copyright (c) 2010 Bradley P. Allen

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.