#!/usr/bin/python
# -*- coding: utf-8 -*-
'''JSON-LD Processor

This module implements a document-based (non-streaming) JSON-LD processor.
JSON-LD is a JSON representation format for Linked Data. A public working 
draft of a potential specification of JSON-LD is available at: 

    http://json-ld.org/spec/latest/
    
This is an experimental implementation, written to support work in 
understanding and helping to refine the draft specification. 
Therefore, one should expect rough but not complete compliance with 
the latest draft.
'''

__version__ = "0.1"
__author__ = 'Bradley P. Allen'
__email__ = "bradley.p.allen@gmail.com"
__credits__ = "Thanks to Manu Sporny and Mark Birbeck for drafting the JSON-LD specification."

import re, uuid, simplejson as json

class Processor(object):
    '''
    Defines a class for a JSON-LD processor, as specified in http://json-ld.org/spec/latest/.
    '''
    
    def __init__(self, context=None):
        '''
        Creates a JSON-LD Processor.

        Keyword arguments:
        context -- a Python dictionary providing the specification of a default context for the processor. 

        If context is None, the default context is equivalent to the following JSON-LD context:
        
        { 
          "#": {
                 "__vocab__": "http://example.org/default-vocab#",
                 "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                 "xsd": "http://www.w3.org/2001/XMLSchema#",
                 "dc": "http://purl.org/dc/terms/",
                 "skos": "http://www.w3.org/2004/02/skos/core#",
                 "foaf": "http://xmlns.com/foaf/0.1/",
                 "sioc": "http://rdfs.org/sioc/ns#",
                 "cc": "http://creativecommons.org/ns#",
                 "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
                 "vcard": "http://www.w3.org/2006/vcard/ns#",
                 "cal": "http://www.w3.org/2002/12/cal/ical#",
                 "doap": "http://usefulinc.com/ns/doap#",
                 "Person": "http://xmlns.com/foaf/0.1/Person",
                 "name": "http://xmlns.com/foaf/0.1/name",
                 "homepage": "http://xmlns.com/foaf/0.1/homepage"
                }
        }
        
        Returns: an instance of json_ld_processor.Processor.

        '''
        if context:
            self.__default_context = context
        else:
            self.__default_context = {
                                      "__vocab__": "http://example.org/default-vocab#",
                                      "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                      "xsd": "http://www.w3.org/2001/XMLSchema#",
                                      "dc": "http://purl.org/dc/terms/",
                                      "skos": "http://www.w3.org/2004/02/skos/core#",
                                      "foaf": "http://xmlns.com/foaf/0.1/",
                                      "sioc": "http://rdfs.org/sioc/ns#",
                                      "cc": "http://creativecommons.org/ns#",
                                      "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
                                      "vcard": "http://www.w3.org/2006/vcard/ns#",
                                      "cal": "http://www.w3.org/2002/12/cal/ical#",
                                      "doap": "http://usefulinc.com/ns/doap#",
                                      "Person": "http://xmlns.com/foaf/0.1/Person",
                                      "name": "http://xmlns.com/foaf/0.1/name",
                                      "homepage": "http://xmlns.com/foaf/0.1/homepage"
                                     }
        self.__curie_pattern = re.compile("^\w+\:\w+$")
        self.__iri_pattern = re.compile("^(<?)(\w+)\:(/?)(/?)([^>\s]+)(>?)$")
        
    def triples(self, doc):
        '''
        An iterator that yields triples by deserializing a JSON_LD document.
        
        Arguments:
        doc -- a str instance containing a JSON_LD document.
        
        Returns: an iterator.
        
        Each triple is a Python dictionary with keys "subj", "prop" and "obj", each
        with values of the triple's subject, property and object, respectively.
        
        For example, the JSON-LD document
        
        {
          "#": {"foaf": "http://xmlns.com/foaf/0.1/"},
          "@": "<http://example.org/people#john>",
          "a": "foaf:Person",
          "foaf:name" : "John Lennon"
        }
        
        yields the following triples
        
        { 
          'obj': 'http://xmlns.com/foaf/0.1/Person', 
          'subj': 'http://example.org/people#john', 
          'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        }
        { 'obj': 'John Lennon', 
          'subj': 'http://example.org/people#john', 
          'prop': 'http://xmlns.com/foaf/0.1/name' 
        }
        
        which can be serialized as follows in N-Triples format
        
        <http://example.org/people#john>
           <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
             <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#john>
           <http://xmlns.com/foaf/0.1/name>
            "John Lennon" .
        '''
        item = json.loads(doc)
        return self.__triples(item, context=self.__default_context)

    def __triples(self, item, context=None):
        '''
        Returns an iterator that yields triples expressed by an item.
        
        An item can be a Python dictionary or list, generated by deserializing a str 
        instance of a JSON_LD document initially supplied in a call to the public 
        function triples().
        '''
        #
        # Three cases to consider: item is a 1) object, 2) array, or 3) a boolean, integer, 
        # float, string, or null
        #
        # Case 1: item is an object (i.e., an associative array)
        #
        if type(item).__name__ == 'dict': # if we have an object
            #
            # Merge contexts if necessary
            #
            if item.has_key("#"): # if it has a local context
                context = self.__merge_contexts(item["#"], context) # merge it into context
            #
            # Determine the subject
            #
            if item.has_key("@"): # if item has a reference to a resource
                subj = item["@"]  # set subj to the reference
                if type(subj).__name__ == 'dict': # if subj is an object
                    for t in self.__triples(subj, context): # recurse
                        yield t # yielding each resulting triple
                    subj = subj["@"] # and set subj to the resource referenced by the object
                elif type(subj).__name__ == 'list': # otherwise if subj is an array
                    for element in subj: # then for each element in the array
                        for t in self.__triples(element, context): # recurse
                            yield t # yielding each resulting triple
                    subj = "_:" + uuid.uuid4().hex # and set subj to a auto-generated bnode
                elif subj: # otherwise, subj is a (Unicode) string
                    subj = self.__term_to_iri(subj, context) # so we map subj to an IRI based on context
                else:
                    pass
            else: # otherwise, we have no reference to a resource
                subj = "_:" + uuid.uuid4().hex # so we set subj to a auto-generated bnode
                item['@'] = subj # and add that key-value pair to the object (for use when we come back from a recursion)
            #
            # Process the key-value pairs
            #
            for key in item:
                if key not in ["#", "@"]: # ignore "#" and "@" since we dealt with them above
                    #
                    # Determine the property
                    #
                    if key == "a": # if we have a type statement
                        prop = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" # set prop to IRI for rdf:type
                    else: # otherwise key is another property 
                        prop = self.__term_to_iri(key, context) # so we map it to an IRI based on context
                    #
                    # Determine the object and yield a triple, recursing if necessary
                    #
                    obj = item[key] # set obj to the key value of the property
                    if type(obj).__name__ == 'dict': # if obj is an object
                        for t in self.__triples(obj, context): # recurse
                            yield t # yielding each resulting triple
                        # and then yield <subj, prop, obj['@']>
                        yield { "subj": subj, "prop": prop, "obj": self.__process_object(obj["@"], context) } 
                    elif type(obj).__name__ == 'list': # otherwise if obj is an array
                        for element in obj: # then for each element in the array
                            # if the element is an array or object
                            if type(element).__name__ == 'list' or type(element).__name__ == 'dict': 
                                for t in self.__triples(element, context): # recurse
                                    yield t # yielding each resulting triple
                                if type(element).__name__ == 'dict': # and if the element is an object
                                    # then yield <subj, prop, element['@']>
                                    yield { "subj": subj, "prop": prop, "obj": self.__process_object(element["@"], context) } 
                            elif element: # otherwise the element is a boolean, integer, float, or string
                                # and we yield <subj, prop, element>
                                yield { "subj": subj, "prop": prop, "obj": self.__process_object(element, context) } 
                    elif obj: # otherwise obj is a boolean, integer, float, or string
                        # and we yield <subj, prop, obj>
                        yield { "subj": subj, "prop": prop, "obj": self.__process_object(obj, context) }                         
                    else: # otherwise obj is a null
                        pass # and we yield nothing
        #
        # Case 2: item is an array
        #
        elif type(item).__name__ == 'list':
            for element in item: # for each element in the array
                for t in self.__triples(element, context): # recurse
                    yield t # yielding each resulting triple
        #
        # Case 3: item is a boolean, integer, float, string, or null
        #
        else: # since there are no key-value pairs or elements to iterate over
            pass # we don't yield any triples
        
    def __merge_contexts(self, local_context, active_context):
        '''
        Returns a context that is the result of merging local_context into active_context.
        
        Merging is defined as in Step 2.1 of the JSON-LD Processing Algorithm in 
        http://json-ld.org/spec/latest/. 
        '''
        context = {}
        for prefix in active_context.keys():
            context[prefix] = active_context[prefix]
        for prefix in local_context.keys():
            context[prefix] = local_context[prefix]
        return context

    def __process_object(self, obj, context):
        '''
        Returns an object value of a triple, given a JSON-LD associative array key value.
        '''
        if type(obj).__name__ in ['str', 'unicode'] and (self.__curie_pattern.match(obj) or self.__iri_pattern.match(obj) or context.has_key(obj)):
            return self.__term_to_iri(obj, context)
        else:
            return self.__value_to_typed_literal(obj)
        
    def __term_to_iri(self, term, context):
        '''
        Returns an IRI as an object for a triple, given a JSON-LD associative array key value that is a term.
        
        A term is either a IRI, an IRI wrapped in angle brackets, a CURIE, a blank node or a string that occurs as a key in the context.
        Specifications referenced in comments: [1] http://www.w3.org/TR/curie, [2] http://www.ietf.org/rfc/rfc3987.txt.
        '''
        m = self.__iri_pattern.match(term)
        if m: # there's something and a colon followed by something
            if m.group(1) == '<' and m.group(6) == '>': # if it is wrapped in angle brackets
                return term.strip('<>') # then assume it is an IRI, strip the angle brackets and return it
            if m.group(3) == '/': # looks like an irrelative-ref as defined in [2], not wrapped in angle brackets
                return term # so assume it's already an IRI
            if context.has_key(m.group(2)): # otherwise, since we have a binding for the prefix
                return context[m.group(2)] + m.group(5) # we concatenate the prefix IRI to the term to get an absolute IRI
            elif m.group(2) == '_': # otherwise if this is a blank node
                return term # we return it directly
            else: # otherwise we have prefix that is not the context
                raise Exception('The current context is missing a match for "%s" in "%s"' % (m.group(2), term))
        else: # otherwise this must be a CURIE reference not preceded by a prefix and a colon
            if context.has_key(term): # if context contains term as a key
                return context[term] # return the key value IRI
            elif context.has_key("__vocab__"): # otherwise if we have a default prefix IRI
                return context["__vocab__"] + term # we concatenate the __vocab__ prefix IRI to the term to get an IRI
            else: # otherwise we complain
                raise Exception("The current context is missing a __vocab__ prefix")
            
    def __value_to_typed_literal(self, value):
        '''
        Returns a typed literal as an object for a triple, given a JSON-LD associative array key value.
        '''
        value_type = type(value).__name__
        if value_type in ['str', 'unicode']:
            # check for lang
            # check for datatype
            return value
        elif value_type == 'bool':
            if value:
                return "true^^http://www.w3.org/2001/XMLSchema#boolean"
            else:
                return "false^^http://www.w3.org/2001/XMLSchema#boolean"
        elif value_type == 'float':
            return ("%f" % value) + "^^http://www.w3.org/2001/XMLSchema#decimal"
        elif value_type in [ 'int', 'long']:
            return ("%d" % value) + "^^http://www.w3.org/2001/XMLSchema#integer"
        else:
            raise Exception("Unknown literal type: %s" % value_type)
    
    
if __name__ == "__main__":
    import unittest

    class TestProcessor(unittest.TestCase):
        '''
        Defines a unittest test processor for automated unit testing of the JSON-LD processor.
        Tests are largely drawn from examples in the specification at http://json-ld.org/spec/latest/,
        but also include some based on individual and group conversations.
        
        Each test case simply takes a JSON-LD document, deserializes it using triples(), 
        and asserts that the generated list of triples is the same as a target list of triples. 
        '''
        
        def triple_in_graph(self, triple, graph):
            '''
            Returns True if a triple matches a triple in a graph (i.e., list of triples).
            '''
            bnode_pattern = "^_\:\w+$"
            s = triple['subj']
            p = triple['prop']
            o = triple['obj']            
            for t in graph:
                subj_bnode = (re.match(bnode_pattern, s) and re.match(bnode_pattern, t['subj']))
                obj_bnode = (re.match(bnode_pattern, o) and re.match(bnode_pattern, t['obj']))
                subj_eq = (s == t['subj'])
                obj_eq = (o == t['obj'])
                subj_match = (subj_bnode or subj_eq)
                prop_match = (p == t['prop'])
                obj_match = (obj_bnode or obj_eq)
                if subj_match and prop_match and obj_match:
                    return True
            return False
        
        def graph_equal(self, graph1, graph2):
            '''
            Returns True if two graphs (i.e., lists of triples) are equivalent.
            
            Two graphs are equivalent iff they have the same number of triples and each triple 
            in one graph matches a triple in the other.
            '''
            if len(graph1) != len(graph2):
                return False
            for triple in graph1:
                if not self.triple_in_graph(triple, graph2):
                    return False
            return True
        
        def json_ld_processing_test_case(self, doc, target_graph):
            '''
            Asserts that the graph generated from a JSON-LD item is equivalent to a target graph.
            '''
            p = Processor()
            generated_graph = [ t for t in p.triples(doc) ]
            self.assertTrue(self.graph_equal(target_graph, generated_graph))

        def test_json_ld_org_landing_page_example(self):
            doc = '{ "#": {"foaf": "http://xmlns.com/foaf/0.1/"}, "@": "<http://example.org/people#john>", "a": "foaf:Person", "foaf:name" : "John Lennon" }'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': 'http://example.org/people#john', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'John Lennon', 'subj': 'http://example.org/people#john', 'prop': 'http://xmlns.com/foaf/0.1/name'}]
            self.json_ld_processing_test_case(doc, target_graph)
                       
        def test_json_ld_spec_section_2_2_example_1(self):
            doc = '{ "a": "Person", "name": "Manu Sporny", "homepage": "http://manu.sporny.org/" }'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:7b07d63c35ca4062b9fcc1f73cf6fab2', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'http://manu.sporny.org/', 'subj': '_:7b07d63c35ca4062b9fcc1f73cf6fab2', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': 'Manu Sporny', 'subj': '_:7b07d63c35ca4062b9fcc1f73cf6fab2', 'prop': 'http://xmlns.com/foaf/0.1/name'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_2_3_example_1(self):
            doc = '{ "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "http://xmlns.com/foaf/0.1/Person", "http://xmlns.com/foaf/0.1/name": "Manu Sporny", "http://xmlns.com/foaf/0.1/homepage": "<http://manu.sporny.org>" }'
            target_graph = [{'obj': 'Manu Sporny', 'subj': '_:d26d82bfda1f43dd9391ea14bda492b8', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'http://manu.sporny.org', 'subj': '_:d26d82bfda1f43dd9391ea14bda492b8', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:d26d82bfda1f43dd9391ea14bda492b8', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section__2_4_example_1(self):
            doc = '{ "rdf:type": "foaf:Person", "foaf:name": "Manu Sporny", "foaf:homepage": "<http://manu.sporny.org/>", "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>" }'
            target_graph = [{'obj': 'http://twitter.com/account/profile_image/manusporny', 'subj': '_:c8ad4c41d8d64452ae445ad98ca000c1', 'prop': 'http://rdfs.org/sioc/ns#avatar'}, {'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:c8ad4c41d8d64452ae445ad98ca000c1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Manu Sporny', 'subj': '_:c8ad4c41d8d64452ae445ad98ca000c1', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'http://manu.sporny.org/', 'subj': '_:c8ad4c41d8d64452ae445ad98ca000c1', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_2_4_example_2(self):
            doc = '{ "#": { "myvocab": "http://example.org/myvocab#" }, "a": "foaf:Person", "foaf:name": "Manu Sporny", "foaf:homepage": "<http://manu.sporny.org/>", "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>", "myvocab:credits": 500 }'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:4e87a73a3992414ea46edc49057e22c6', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Manu Sporny', 'subj': '_:4e87a73a3992414ea46edc49057e22c6', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': '500^^http://www.w3.org/2001/XMLSchema#integer', 'subj': '_:4e87a73a3992414ea46edc49057e22c6', 'prop': 'http://example.org/myvocab#credits'}, {'obj': 'http://manu.sporny.org/', 'subj': '_:4e87a73a3992414ea46edc49057e22c6', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': 'http://twitter.com/account/profile_image/manusporny', 'subj': '_:4e87a73a3992414ea46edc49057e22c6', 'prop': 'http://rdfs.org/sioc/ns#avatar'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_3_1_example_2(self):
            doc = '[ { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode1", "a": "foaf:Person", "foaf:homepage": "<http://example.com/bob/>", "foaf:name": "Bob" }, { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode2", "a": "foaf:Person", "foaf:homepage": "<http://example.com/eve/>", "foaf:name": "Eve" }, { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode3", "a": "foaf:Person", "foaf:homepage": "<http://example.com/manu/>", "foaf:name": "Manu" } ]'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:bnode1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Bob', 'subj': '_:bnode1', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'http://example.com/bob/', 'subj': '_:bnode1', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:bnode2', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Eve', 'subj': '_:bnode2', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'http://example.com/eve/', 'subj': '_:bnode2', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': '_:bnode3', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Manu', 'subj': '_:bnode3', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'http://example.com/manu/', 'subj': '_:bnode3', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_3_2_example_2(self):
            doc = '{ "#": { "vcard": "http://microformats.org/profile/hcard#vcard", "url": "http://microformats.org/profile/hcard#url", "fn": "http://microformats.org/profile/hcard#fn" }, "@": "_:bnode1", "a": "vcard", "url": "<http://tantek.com/>", "fn": "Tantek Çelik" }'
            target_graph = [{'obj': 'http://microformats.org/profile/hcard#vcard', 'subj': '_:bnode1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'http://tantek.com/', 'subj': '_:bnode1', 'prop': 'http://microformats.org/profile/hcard#url'}, {'obj': u'Tantek \xc7elik', 'subj': '_:bnode1', 'prop': 'http://microformats.org/profile/hcard#fn'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_3_3_example_2(self):
            doc = '[ { "@": "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>", "a": "http://purl.org/vocab/frbr/core#Work", "http://purl.org/dc/terms/title": "Just a Geek", "http://purl.org/dc/terms/creator": "Whil Wheaton", "http://purl.org/vocab/frbr/core#realization": [ "<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>" ]  }, { "@": "<http://purl.oreilly.com/products/9780596007683.BOOK>", "a": "<http://purl.org/vocab/frbr/core#Expression>", "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/BOOK>" },  { "@": "<http://purl.oreilly.com/products/9780596802189.EBOOK>", "a": "http://purl.org/vocab/frbr/core#Expression", "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/EBOOK>" } ]'
            target_graph = [{'obj': 'http://purl.org/vocab/frbr/core#Work', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Just a Geek', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/dc/terms/title'}, {'obj': 'Whil Wheaton', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/dc/terms/creator'}, {'obj': 'http://purl.oreilly.com/products/9780596007683.BOOK', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/vocab/frbr/core#realization'}, {'obj': 'http://purl.oreilly.com/products/9780596802189.EBOOK', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/vocab/frbr/core#realization'}, {'obj': 'http://purl.org/vocab/frbr/core#Expression', 'subj': 'http://purl.oreilly.com/products/9780596007683.BOOK', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'http://purl.oreilly.com/product-types/BOOK', 'subj': 'http://purl.oreilly.com/products/9780596007683.BOOK', 'prop': 'http://purl.org/dc/terms/type'}, {'obj': 'http://purl.org/vocab/frbr/core#Expression', 'subj': 'http://purl.oreilly.com/products/9780596802189.EBOOK', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'http://purl.oreilly.com/product-types/EBOOK', 'subj': 'http://purl.oreilly.com/products/9780596802189.EBOOK', 'prop': 'http://purl.org/dc/terms/type'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_3_3_example_2_variant(self):
            doc = '{ "#" : { "__vocab__" : "http://www.w3.org/1999/xhtml/microdata#", "frbr" : "http://purl.org/vocab/frbr/core#", "dc" : "http://purl.org/dc/terms/" }, "a" : "frbr:Work", "@" : "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>", "dc:title" : "Just a Geek", "dc:creator" : "Whil Wheaton", "frbr:realization" : [ "<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>" ] }'
            target_graph = [{'obj': 'http://purl.org/vocab/frbr/core#Work', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'Whil Wheaton', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/dc/terms/creator'}, {'obj': 'Just a Geek', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/dc/terms/title'}, {'obj': 'http://purl.oreilly.com/products/9780596007683.BOOK', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/vocab/frbr/core#realization'}, {'obj': 'http://purl.oreilly.com/products/9780596802189.EBOOK', 'subj': 'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://purl.org/vocab/frbr/core#realization'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_5_1_to_7_examples(self):
            doc = '{ "foaf:homepage": "<http://manu.sporny.org>", "@": "<http://example.org/people#joebob>", "a": "<http://xmlns.com/foaf/0.1/Person>", "foaf:name": "Mark Birbeck", "foaf:name": "花澄@ja", "dc:modified": "2010-05-29T14:17:39+02:00^^xsd:dateTime", "foaf:nick": ["stu", "groknar", "radface"] }'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': 'http://example.org/people#joebob', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'\u82b1\u6f84@ja', 'subj': 'http://example.org/people#joebob', 'prop': 'http://xmlns.com/foaf/0.1/name'}, {'obj': 'stu', 'subj': 'http://example.org/people#joebob', 'prop': 'http://xmlns.com/foaf/0.1/nick'}, {'obj': 'groknar', 'subj': 'http://example.org/people#joebob', 'prop': 'http://xmlns.com/foaf/0.1/nick'}, {'obj': 'radface', 'subj': 'http://example.org/people#joebob', 'prop': 'http://xmlns.com/foaf/0.1/nick'}, {'obj': 'http://manu.sporny.org', 'subj': 'http://example.org/people#joebob', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'obj': '2010-05-29T14:17:39+02:00^^xsd:dateTime', 'subj': 'http://example.org/people#joebob', 'prop': 'http://purl.org/dc/terms/modified'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_5_8_example_1(self):
            doc = '{ "@": "<http://example.org/articles/8>", "dc:modified": ["2010-05-29T14:17:39+02:00^^xsd:dateTime", "2010-05-30T09:21:28-04:00^^xsd:dateTime"] }'
            target_graph = [{'obj': '2010-05-29T14:17:39+02:00^^xsd:dateTime', 'subj': 'http://example.org/articles/8', 'prop': 'http://purl.org/dc/terms/modified'}, {'obj': '2010-05-30T09:21:28-04:00^^xsd:dateTime', 'subj': 'http://example.org/articles/8', 'prop': 'http://purl.org/dc/terms/modified'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_5_9_10_and_11_examples_variant(self):
            doc = '{ "@": "_:foo", "code": "\\\<foobar\\\^\\\^2\\\>", "cups": 5.3, "protons": 12, "active": true }'
            target_graph = [{'obj': '5.300000^^http://www.w3.org/2001/XMLSchema#decimal', 'subj': '_:foo', 'prop': 'http://example.org/default-vocab#cups'}, {'obj': '\\<foobar\\^\\^2\\>', 'subj': '_:foo', 'prop': 'http://example.org/default-vocab#code'}, {'obj': '12^^http://www.w3.org/2001/XMLSchema#integer', 'subj': '_:foo', 'prop': 'http://example.org/default-vocab#protons'}, {'obj': 'true^^http://www.w3.org/2001/XMLSchema#boolean', 'subj': '_:foo', 'prop': 'http://example.org/default-vocab#active'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_json_ld_spec_section_6_1_example_2(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": [ { "@": "<http://example.org/people#john>", "a": "foaf:Person" }, { "@": "<http://example.org/people#jane>", "a": "foaf:Person" } ] }'
            target_graph = [{'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': 'http://example.org/people#john', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': 'http://xmlns.com/foaf/0.1/Person', 'subj': 'http://example.org/people#jane', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_nested_associative_array(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode1", "a": "foaf:Person", "foaf:homepage": "<http://example.com/bob/>", "foaf:name": "Bob", "foaf:knows": { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode2", "a": "foaf:Person", "foaf:homepage": "<http://example.com/eve/>", "foaf:name": "Eve" } }'
            target_graph = [{'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode2', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Eve', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/eve/', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'obj': u'_:bnode2', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'obj': u'http://example.com/bob/', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_nested_associative_array_implicit_bnodes(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "a": "foaf:Person", "foaf:homepage": "<http://example.com/bob/>", "foaf:name": "Bob", "foaf:knows": {"a": "foaf:Person", "foaf:homepage": "<http://example.com/eve/>", "foaf:name": "Eve" } }'
            target_graph = [{'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': '_:a6cf053c53854e0caa60c0824e53872a', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Bob', 'subj': '_:a6cf053c53854e0caa60c0824e53872a', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': '_:d790fbce025648a88ecd8d1f06c99cb6', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Eve', 'subj': '_:d790fbce025648a88ecd8d1f06c99cb6', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/eve/', 'subj': '_:d790fbce025648a88ecd8d1f06c99cb6', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'obj': '_:d790fbce025648a88ecd8d1f06c99cb6', 'subj': '_:a6cf053c53854e0caa60c0824e53872a', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'obj': u'http://example.com/bob/', 'subj': '_:a6cf053c53854e0caa60c0824e53872a', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_nested_associative_arrays_list(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode1", "a": "foaf:Person", "foaf:homepage": "<http://example.com/bob/>", "foaf:name": "Bob", "foaf:knows": [ { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode2", "a": "foaf:Person", "foaf:homepage": "<http://example.com/eve/>", "foaf:name": "Eve" }, { "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "@": "_:bnode3", "a": "foaf:Person", "foaf:homepage": "<http://example.com/manu/>", "foaf:name": "Manu" } ] }'
            target_graph = [{'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode2', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Eve', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/eve/', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'obj': u'_:bnode2', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode3', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Manu', 'subj': u'_:bnode3', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/manu/', 'subj': u'_:bnode3', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'obj': u'_:bnode3', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'obj': u'http://example.com/bob/', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_associative_array_without_explicit_subject_as_subject(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "foaf:homepage": "<http://example.com/bob/>", "@": { "a": "foaf:Person", "foaf:name": "Bob" } }'
            target_graph = [{'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': '_:98c0d50dcdc24b3cb13f1d037d750577', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Bob', 'subj': '_:98c0d50dcdc24b3cb13f1d037d750577', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/bob/', 'subj': '_:98c0d50dcdc24b3cb13f1d037d750577', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

        def test_associative_array_with_bnode_subject_as_subject(self):
            doc = '{ "#": { "foaf": "http://xmlns.com/foaf/0.1/" }, "foaf:homepage": "<http://example.com/bob/>", "@": { "@": "_:bnode1", "a": "foaf:Person", "foaf:name": "Bob" } }'
            target_graph = [{'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': u'_:bnode1', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'obj': u'http://example.com/bob/', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
            self.json_ld_processing_test_case(doc, target_graph)

    unittest.main() 
