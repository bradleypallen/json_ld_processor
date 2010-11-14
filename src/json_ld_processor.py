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

__version__ = "0.2"
__author__ = 'Bradley P. Allen'
__email__ = "bradley.p.allen@gmail.com"
__credits__ = "Thanks to Manu Sporny and Mark Birbeck for drafting the JSON-LD specification."

import re, uuid, json, urlparse

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
        self.__curie_pattern = re.compile("^(?P<prefix>\w+)\:(?P<reference>\w+)$")
        self.__bnode_pattern = re.compile("^_\:\w+$")
        self.__iri_pattern = re.compile("^<?(?P<iri>(\w+)\:(/?)(/?)([^>\s]+))>?$")
        self.__absolute_iri_pattern = re.compile("^(?P<iri>(\w+)\:(/?)(/?)([^>\s]+))$")
        self.__wrapped_absolute_iri_pattern = re.compile("^<(?P<iri>(\w+)\:(/?)(/?)([^>\s]+))>$")
        self.__wrapped_relative_iri_pattern = re.compile("^<(?P<iri>[^\:>\s]+)>$")
        self.__lang_pattern = re.compile("^(?P<literal>.+)@(?P<lang>[a-zA-Z][a-zA-Z0-9\-]+)$")
        self.__typed_literal_pattern = re.compile("^(?P<literal>.+)\^\^(?P<datatype>.+)$")
        self.__datetime_pattern = re.compile("^(?P<year>\d\d\d\d)([-])?(?P<month>\d\d)([-])?(?P<day>\d\d)((T|\s+)(?P<hour>\d\d)(([:])?(?P<minute>\d\d)(([:])?(?P<second>\d\d)(([.])?(?P<fraction>\d+))?)?)?)?((?P<tzzulu>Z)|(?P<tzoffset>[-+])(?P<tzhour>\d\d)([:])?(?P<tzminute>\d\d))?$")
        
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
            'objtype': 'resource', 
            'subj': u'http://example.org/people#john', 
            'obj': u'http://xmlns.com/foaf/0.1/Person', 
            'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        }, 
        {
            'objtype': 'literal', 
            'datatype': 'http://www.w3.org/2001/XMLSchema#string', 
            'obj': u'John Lennon', 
            'subj': u'http://example.org/people#john', 
            'prop': u'http://xmlns.com/foaf/0.1/name'
        }
        
        which can be serialized as follows in N-Triples format
        
        <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#john> <http://xmlns.com/foaf/0.1/name> "John Lennon" .
        '''
        item = json.loads(doc)
        return self.__triples(item, context=self.__default_context)

    def __triples(self, item, context=None):
        '''
        Returns a generator that yields triples expressed by an item.
        
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
                    subj = self.__resource(subj, context) # so we map subj to an IRI based on context
                else:
                    pass
            else: # otherwise, we have no reference to a resource
                subj = "_:" + uuid.uuid4().hex # so we set subj to a auto-generated bnode
                item['@'] = subj # and add that key-value pair to the object (for when a recursion returns)
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
                        prop = self.__property(key, context) # so we map it to an IRI based on context
                    #
                    # Determine the object and yield a triple, recursing if necessary
                    #
                    obj = item[key] # set obj to the key value of the property
                    if type(obj).__name__ == 'dict': # if obj is an object
                        for t in self.__triples(obj, context): # recurse
                            yield t # yielding each resulting triple
                        # and then yield <subj, prop, obj['@']>
                        yield self.__triple(subj, prop, obj["@"], context)
                    elif type(obj).__name__ == 'list': # otherwise if obj is an array
                        for element in obj: # then for each element in the array
                            # if the element is an array or object
                            if type(element).__name__ == 'list' or type(element).__name__ == 'dict': 
                                for t in self.__triples(element, context): # recurse
                                    yield t # yielding each resulting triple
                                if type(element).__name__ == 'dict': # and if the element is an object
                                    # then yield <subj, prop, element['@']>
                                    yield self.__triple(subj, prop, element["@"], context)
                            elif element: # otherwise the element is a boolean, integer, float, or string
                                # and we yield <subj, prop, element>
                                yield self.__triple(subj, prop, element, context)
                    elif obj: # otherwise obj is a boolean, integer, float, or string
                        # and we yield <subj, prop, obj>
                        yield self.__triple(subj, prop, obj, context)
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

    def __property(self, key, context):
        '''
        Returns an IRI as a property for a triple, given a JSON-LD object key.
        Specifications referenced in comments: [1] http://www.w3.org/TR/curie, [2] http://www.ietf.org/rfc/rfc3987.txt.
        '''
        m = self.__iri_pattern.match(key)
        if m: # there's something and a colon followed by something
            if m.group(1) == '<' and m.group(6) == '>': # if it is wrapped in angle brackets
                return key.strip('<>') # then assume it is an IRI, strip the angle brackets and return it
            elif m.group(3) == '/': # looks like an irrelative-ref as defined in [2], not wrapped in angle brackets
                return key # so assume it's already an IRI
            elif context.has_key(m.group(2)): # otherwise, since we have a binding for the prefix
                return context[m.group(2)] + m.group(5) # we append the key to the prefix IRI
            elif m.group(2) == '_': # otherwise if this is a blank node
                return key # we return it directly
            else: # otherwise we have prefix that is not in the context
                raise Exception('The current context is missing a match for "%s" in "%s"' % (m.group(2), key))
        else: # otherwise this must be a key or a relative IRI
            if context.has_key(key): # if context contains key as a key
                return context[key] # return the key value IRI
            elif context.has_key("#vocab"): # otherwise if we have a #vocab IRI
                return context["#vocab"] + key # we append the key to the #vocab IRI
            else: # otherwise we complain
                raise Exception("The current context is missing a #vocab prefix")
            
    def __triple(self, subj, prop, obj, context):
        '''
        Returns an object value of a triple, given a JSON-LD object key value.
        '''
        if type(obj).__name__ in ['str', 'unicode'] and (context.has_key(obj) or self.__bnode_pattern.match(obj) or self.__curie_pattern.match(obj) or self.__wrapped_absolute_iri_pattern.match(obj) or self.__wrapped_relative_iri_pattern.match(obj)):
            return self.__resource_valued_triple(subj, prop, obj, context)
        else:
            return self.__literal_valued_triple(subj, prop, obj, context)
        
    def __resource_valued_triple(self, subj, prop, obj, context):
        '''
        Returns a dict representing a resource as an object.
        '''
        return { "subj": subj, "prop": prop, "objtype": "resource", "obj": self.__resource(obj, context) }

    def __resource(self, value, context):
        '''
        Returns a resource, which is either an absolute IRI or a blank node.
        '''
        wrapped_absolute_iri = self.__wrapped_absolute_iri_pattern.match(value)
        wrapped_relative_iri = self.__wrapped_relative_iri_pattern.match(value)
        curie = self.__curie_pattern.match(value)
        bnode = self.__bnode_pattern.match(value)
        if context.has_key(value):
            return context[value]
        elif bnode:
            return value
        elif curie:
            if context.has_key(curie.group('prefix')):
                return context[curie.group('prefix')] + curie.group('reference')
            elif context.has_key(curie.group('reference')):
                return context[curie.group('reference')]
            else:
                raise Exception('The current context is missing a match for "%s" or "%s" in "%s"' % (curie.group('prefix'), curie.group('reference'), value))
        elif wrapped_absolute_iri:
            if context.has_key('#base'):
                base = context['#base']
            else:
                base = ''
            return urlparse.urljoin(base, wrapped_absolute_iri.group('iri'))
        elif wrapped_relative_iri:
            if context.has_key('#base'):
                return urlparse.urljoin(context['#base'], wrapped_relative_iri.group('iri'))
            else:
                raise Exception("The current context is missing a #base prefix")
        else:
            raise Exception("%s is neither a CURIE, blank node nor a wrapped IRI" % (value))
            
    def __datatype(self, value, context):
        '''
        Returns a resource, which is either an absolute IRI or a blank node.
        '''
        absolute_iri = self.__absolute_iri_pattern.match(value)
        curie = self.__curie_pattern.match(value)
        if curie:
            if context.has_key(curie.group('prefix')):
                return context[curie.group('prefix')] + curie.group('reference')
            elif context.has_key(curie.group('reference')):
                return context[curie.group('reference')]
            else:
                raise Exception('The current context is missing a match for "%s" or "%s" in "%s"' % (curie.group('prefix'), curie.group('reference'), value))
        elif absolute_iri:
            return absolute_iri.group('iri')
        else:
            raise Exception("%s is neither a CURIE, blank node nor a wrapped IRI" % (value))
        
    def __unescape(self, str):
        return str.replace("\\<", "<").replace("\\>", ">").replace("\\@", "@").replace("\\#", "#").replace("\\:", ":").replace("\\^", "^")        
        
    def __literal_valued_triple(self, subj, prop, value, context):
        '''
        Returns a dict representing a triple with a typed literal as an object.
        '''
        triple = { "subj": subj, "prop": prop, "objtype": "literal" }
        value_type = type(value).__name__
        if value_type == 'bool':
            if value:
                triple["obj"] = "true"
                triple["datatype"] = "http://www.w3.org/2001/XMLSchema#boolean"
            else:
                triple["obj"] = "false"
                triple["datatype"] = "http://www.w3.org/2001/XMLSchema#boolean"
        elif value_type in ['int', 'long']:
            triple["obj"] = ("%d" % value)
            triple["datatype"] = "http://www.w3.org/2001/XMLSchema#integer"
        elif value_type == 'float':
            triple["obj"] = ("%f" % value)
            triple["datatype"] = "http://www.w3.org/2001/XMLSchema#float"
        elif value_type in ['str', 'unicode']:
            typed_literal_match = self.__typed_literal_pattern.match(value)
            lang_match = self.__lang_pattern.match(value)
            if typed_literal_match:
                triple["obj"] = self.__unescape(typed_literal_match.group(1))
                triple["datatype"] = self.__datatype(typed_literal_match.group(2), context)
            elif self.__datetime_pattern.match(value):
                triple["obj"] = self.__unescape(value)
                triple["datatype"] = "http://www.w3.org/2001/XMLSchema#dateTime"
            elif lang_match:
                triple["obj"] = self.__unescape(lang_match.group(1))
                triple["datatype"] = "http://www.w3.org/2001/XMLSchema#string"
                triple["lang"] = lang_match.group(2)
            else:
                triple["obj"] = self.__unescape(value)
                triple["datatype"] = "http://www.w3.org/2001/XMLSchema#string"
        else:
            raise Exception("Value '%s' has unknown literal type: %s" % (value, value_type))
        return triple
    
