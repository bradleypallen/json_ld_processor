#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest, json_ld_processor as jlp
from json_ld_test_utilities import graph_equal

class TestProcessor(unittest.TestCase):
    '''
    Defines a unittest test processor for automated unit testing of the JSON-LD processor.
    Tests are largely drawn from examples in the specification at http://json-ld.org/spec/latest/,
    but also include some based on individual and group conversations.

    Each test case simply takes a JSON-LD document, deserializes it using triples(),
    and asserts that the generated list of triples is the same as a target list of triples.
    '''


    def test_associative_array_with_bnode_subject_as_subject(self):
        '''
        JSON-LD:

        {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "foaf:homepage": "<http://example.com/bob/>",
           "@": { 
                  "@": "_:bnode1",
                  "a": "foaf:Person", 
                  "foaf:name": "Bob" 
                }
        }

        N-Triples:
        _:bnode1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode1 <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:bnode1 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .

        '''
        p = jlp.Processor()
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "foaf:homepage": "<http://example.com/bob/>",   "@": {           "@": "_:bnode1",          "a": "foaf:Person",           "foaf:name": "Bob"         }}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_associative_array_without_explicit_subject_as_subject(self):
        '''
        JSON-LD:

        {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "foaf:homepage": "<http://example.com/bob/>",
           "@": { 
                  "a": "foaf:Person", 
                  "foaf:name": "Bob" 
                }
        }

        N-Triples:
        _:c8229d3d5c854217901a75c48909bcac <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:c8229d3d5c854217901a75c48909bcac <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:c8229d3d5c854217901a75c48909bcac <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .

        '''
        p = jlp.Processor()
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "foaf:homepage": "<http://example.com/bob/>",   "@": {           "a": "foaf:Person",           "foaf:name": "Bob"         }}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': '_:8da681ea75e2471a9bc1280e16de237d', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': '_:8da681ea75e2471a9bc1280e16de237d', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': '_:8da681ea75e2471a9bc1280e16de237d', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_integer(self):
        '''
        JSON-LD:

        42

        N-Triples:

        '''
        p = jlp.Processor()
        doc = '42'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = []
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_org_landing_page_example(self):
        '''
        JSON-LD:

        {
          "#": {"foaf": "http://xmlns.com/foaf/0.1/"},
          "@": "<http://example.org/people#john>",
          "a": "foaf:Person",
          "foaf:name" : "John Lennon"
        }

        N-Triples:
        <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#john> <http://xmlns.com/foaf/0.1/name> "John Lennon" .

        '''
        p = jlp.Processor()
        doc = '{  "#": {"foaf": "http://xmlns.com/foaf/0.1/"},  "@": "<http://example.org/people#john>",  "a": "foaf:Person",  "foaf:name" : "John Lennon"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'http://example.org/people#john', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'John Lennon', 'subj': u'http://example.org/people#john', 'prop': u'http://xmlns.com/foaf/0.1/name'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_2_2_example_1(self):
        '''
        JSON-LD:

        {
          "a": "Person",
          "name": "Manu Sporny",
          "homepage": "http://manu.sporny.org/"
        }

        N-Triples:
        _:cf291ac5d4d443e2af36f9e1d92b2c52 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:cf291ac5d4d443e2af36f9e1d92b2c52 <http://xmlns.com/foaf/0.1/homepage> "http://manu.sporny.org/" .
        _:cf291ac5d4d443e2af36f9e1d92b2c52 <http://xmlns.com/foaf/0.1/name> "Manu Sporny" .

        '''
        p = jlp.Processor()
        doc = '{  "a": "Person",  "name": "Manu Sporny",  "homepage": "http://manu.sporny.org/"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': '_:313103a120fb4a58a36760ee55615ed4', 'obj': 'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'http://manu.sporny.org/', 'subj': '_:313103a120fb4a58a36760ee55615ed4', 'prop': 'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu Sporny', 'subj': '_:313103a120fb4a58a36760ee55615ed4', 'prop': 'http://xmlns.com/foaf/0.1/name'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_2_3_example_1(self):
        '''
        JSON-LD:

        {
          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "http://xmlns.com/foaf/0.1/Person",
          "http://xmlns.com/foaf/0.1/name": "Manu Sporny",
          "http://xmlns.com/foaf/0.1/homepage": "<http://manu.sporny.org>"
        }

        N-Triples:
        _:183c37a92af04884854c5a9510faa3d5 <http://xmlns.com/foaf/0.1/name> "Manu Sporny" .
        _:183c37a92af04884854c5a9510faa3d5 <http://xmlns.com/foaf/0.1/homepage> <http://manu.sporny.org> .
        _:183c37a92af04884854c5a9510faa3d5 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "http://xmlns.com/foaf/0.1/Person" .

        '''
        p = jlp.Processor()
        doc = '{  "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "http://xmlns.com/foaf/0.1/Person",  "http://xmlns.com/foaf/0.1/name": "Manu Sporny",  "http://xmlns.com/foaf/0.1/homepage": "<http://manu.sporny.org>"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu Sporny', 'subj': '_:9abc3739412d4fc6a92282b8a2ddba17', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': '_:9abc3739412d4fc6a92282b8a2ddba17', 'obj': u'http://manu.sporny.org', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'subj': '_:9abc3739412d4fc6a92282b8a2ddba17', 'prop': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_2_4_example_1(self):
        '''
        JSON-LD:

        {
          "rdf:type": "foaf:Person",
          "foaf:name": "Manu Sporny",
          "foaf:homepage": "<http://manu.sporny.org/>",
          "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>"
        }

        N-Triples:
        _:2f8430c80e1f4a35acfb499933728a01 <http://rdfs.org/sioc/ns#avatar> <http://twitter.com/account/profile_image/manusporny> .
        _:2f8430c80e1f4a35acfb499933728a01 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:2f8430c80e1f4a35acfb499933728a01 <http://xmlns.com/foaf/0.1/name> "Manu Sporny" .
        _:2f8430c80e1f4a35acfb499933728a01 <http://xmlns.com/foaf/0.1/homepage> <http://manu.sporny.org/> .

        '''
        p = jlp.Processor()
        doc = '{  "rdf:type": "foaf:Person",  "foaf:name": "Manu Sporny",  "foaf:homepage": "<http://manu.sporny.org/>",  "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': '_:35be066975bf4e02847f13f0094f192c', 'obj': u'http://twitter.com/account/profile_image/manusporny', 'prop': u'http://rdfs.org/sioc/ns#avatar'}, {'objtype': 'resource', 'subj': '_:35be066975bf4e02847f13f0094f192c', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu Sporny', 'subj': '_:35be066975bf4e02847f13f0094f192c', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': '_:35be066975bf4e02847f13f0094f192c', 'obj': u'http://manu.sporny.org/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_2_4_example_2(self):
        '''
        JSON-LD:

        {
          "#": { "myvocab": "http://example.org/myvocab#" },
          "a": "foaf:Person",
          "foaf:name": "Manu Sporny",
          "foaf:homepage": "<http://manu.sporny.org/>",
          "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>",
          "myvocab:credits": 500
        }

        N-Triples:
        _:49bae4d93db1458ca78bdb94c960970c <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:49bae4d93db1458ca78bdb94c960970c <http://xmlns.com/foaf/0.1/name> "Manu Sporny" .
        _:49bae4d93db1458ca78bdb94c960970c <http://example.org/myvocab#credits> "500"^^<http://www.w3.org/2001/XMLSchema#integer> .
        _:49bae4d93db1458ca78bdb94c960970c <http://xmlns.com/foaf/0.1/homepage> <http://manu.sporny.org/> .
        _:49bae4d93db1458ca78bdb94c960970c <http://rdfs.org/sioc/ns#avatar> <http://twitter.com/account/profile_image/manusporny> .

        '''
        p = jlp.Processor()
        doc = '{  "#": { "myvocab": "http://example.org/myvocab#" },  "a": "foaf:Person",  "foaf:name": "Manu Sporny",  "foaf:homepage": "<http://manu.sporny.org/>",  "sioc:avatar": "<http://twitter.com/account/profile_image/manusporny>",  "myvocab:credits": 500}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': '_:c72a7afa7e074a24b27ee2a78c75323f', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu Sporny', 'subj': '_:c72a7afa7e074a24b27ee2a78c75323f', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'obj': '500', 'subj': '_:c72a7afa7e074a24b27ee2a78c75323f', 'prop': u'http://example.org/myvocab#credits'}, {'objtype': 'resource', 'subj': '_:c72a7afa7e074a24b27ee2a78c75323f', 'obj': u'http://manu.sporny.org/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': '_:c72a7afa7e074a24b27ee2a78c75323f', 'obj': u'http://twitter.com/account/profile_image/manusporny', 'prop': u'http://rdfs.org/sioc/ns#avatar'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_3_1_example_2(self):
        '''
        JSON-LD:

        [
         {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "@": "_:bnode1",
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/bob/>",
           "foaf:name": "Bob"
         },
         {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "@": "_:bnode2",
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/eve/>",
           "foaf:name": "Eve"
         },
         {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "@": "_:bnode3",
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/manu/>",
           "foaf:name": "Manu"
         }
        ]

        N-Triples:
        _:bnode1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode1 <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:bnode1 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .
        _:bnode2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode2 <http://xmlns.com/foaf/0.1/name> "Eve" .
        _:bnode2 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/eve/> .
        _:bnode3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode3 <http://xmlns.com/foaf/0.1/name> "Manu" .
        _:bnode3 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/manu/> .

        '''
        p = jlp.Processor()
        doc = '[ {   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode1",   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/bob/>",   "foaf:name": "Bob" }, {   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode2",   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/eve/>",   "foaf:name": "Eve" }, {   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode3",   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/manu/>",   "foaf:name": "Manu" }]'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Eve', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://example.com/eve/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': u'_:bnode3', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu', 'subj': u'_:bnode3', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode3', 'obj': u'http://example.com/manu/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_3_2_example_2(self):
        '''
        JSON-LD:

        {
          "#": 
          {
            "vcard": "http://microformats.org/profile/hcard#vcard",
            "url": "http://microformats.org/profile/hcard#url",
            "fn": "http://microformats.org/profile/hcard#fn"
          },
          "@": "_:bnode1",
          "a": "vcard",
          "url": "<http://tantek.com/>",
          "fn": "Tantek Çelik"
        }

        N-Triples:
        _:bnode1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://microformats.org/profile/hcard#vcard> .
        _:bnode1 <http://microformats.org/profile/hcard#url> <http://tantek.com/> .
        _:bnode1 <http://microformats.org/profile/hcard#fn> "Tantek Çelik" .

        '''
        p = jlp.Processor()
        doc = '{  "#":   {    "vcard": "http://microformats.org/profile/hcard#vcard",    "url": "http://microformats.org/profile/hcard#url",    "fn": "http://microformats.org/profile/hcard#fn"  },  "@": "_:bnode1",  "a": "vcard",  "url": "<http://tantek.com/>",  "fn": "Tantek Çelik"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://microformats.org/profile/hcard#vcard', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://tantek.com/', 'prop': u'http://microformats.org/profile/hcard#url'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Tantek \xc7elik', 'subj': u'_:bnode1', 'prop': u'http://microformats.org/profile/hcard#fn'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_3_3_example_2(self):
        '''
        JSON-LD:

        [
          {
            "@": "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>",
            "a": "http://purl.org/vocab/frbr/core#Work",
            "http://purl.org/dc/terms/title": "Just a Geek",
            "http://purl.org/dc/terms/creator": "Whil Wheaton",
            "http://purl.org/vocab/frbr/core#realization": 
              ["<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>"]
          },
          {
            "@": "<http://purl.oreilly.com/products/9780596007683.BOOK>",
            "a": "<http://purl.org/vocab/frbr/core#Expression>",
            "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/BOOK>"
          },
          {
            "@": "<http://purl.oreilly.com/products/9780596802189.EBOOK>",
            "a": "http://purl.org/vocab/frbr/core#Expression",
            "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/EBOOK>"
          }
        ]

        N-Triples:
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "http://purl.org/vocab/frbr/core#Work" .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/dc/terms/title> "Just a Geek" .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/dc/terms/creator> "Whil Wheaton" .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/vocab/frbr/core#realization> <http://purl.oreilly.com/products/9780596007683.BOOK> .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/vocab/frbr/core#realization> <http://purl.oreilly.com/products/9780596802189.EBOOK> .
        <http://purl.oreilly.com/products/9780596007683.BOOK> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/vocab/frbr/core#Expression> .
        <http://purl.oreilly.com/products/9780596007683.BOOK> <http://purl.org/dc/terms/type> <http://purl.oreilly.com/product-types/BOOK> .
        <http://purl.oreilly.com/products/9780596802189.EBOOK> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "http://purl.org/vocab/frbr/core#Expression" .
        <http://purl.oreilly.com/products/9780596802189.EBOOK> <http://purl.org/dc/terms/type> <http://purl.oreilly.com/product-types/EBOOK> .

        '''
        p = jlp.Processor()
        doc = '[  {    "@": "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>",    "a": "http://purl.org/vocab/frbr/core#Work",    "http://purl.org/dc/terms/title": "Just a Geek",    "http://purl.org/dc/terms/creator": "Whil Wheaton",    "http://purl.org/vocab/frbr/core#realization":       ["<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>"]  },  {    "@": "<http://purl.oreilly.com/products/9780596007683.BOOK>",    "a": "<http://purl.org/vocab/frbr/core#Expression>",    "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/BOOK>"  },  {    "@": "<http://purl.oreilly.com/products/9780596802189.EBOOK>",    "a": "http://purl.org/vocab/frbr/core#Expression",    "http://purl.org/dc/terms/type": "<http://purl.oreilly.com/product-types/EBOOK>"  }]'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'http://purl.org/vocab/frbr/core#Work', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Just a Geek', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': u'http://purl.org/dc/terms/title'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Whil Wheaton', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': u'http://purl.org/dc/terms/creator'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'obj': u'http://purl.oreilly.com/products/9780596007683.BOOK', 'prop': u'http://purl.org/vocab/frbr/core#realization'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'obj': u'http://purl.oreilly.com/products/9780596802189.EBOOK', 'prop': u'http://purl.org/vocab/frbr/core#realization'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/products/9780596007683.BOOK', 'obj': u'http://purl.org/vocab/frbr/core#Expression', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/products/9780596007683.BOOK', 'obj': u'http://purl.oreilly.com/product-types/BOOK', 'prop': u'http://purl.org/dc/terms/type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'http://purl.org/vocab/frbr/core#Expression', 'subj': u'http://purl.oreilly.com/products/9780596802189.EBOOK', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/products/9780596802189.EBOOK', 'obj': u'http://purl.oreilly.com/product-types/EBOOK', 'prop': u'http://purl.org/dc/terms/type'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_3_3_example_2_variant(self):
        '''
        JSON-LD:

        {  
           "#" : { 
                   "__vocab__" : "http://www.w3.org/1999/xhtml/microdata#",
                   "frbr" : "http://purl.org/vocab/frbr/core#",
                   "dc" : "http://purl.org/dc/terms/"
                 },
           "a" : "frbr:Work",
           "@" : "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>",
           "dc:title" : "Just a Geek",
           "dc:creator" : "Whil Wheaton",
           "frbr:realization" : ["<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>"]
        }

        N-Triples:
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/vocab/frbr/core#Work> .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/dc/terms/creator> "Whil Wheaton" .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/dc/terms/title> "Just a Geek" .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/vocab/frbr/core#realization> <http://purl.oreilly.com/products/9780596007683.BOOK> .
        <http://purl.oreilly.com/works/45U8QJGZSQKDH8N> <http://purl.org/vocab/frbr/core#realization> <http://purl.oreilly.com/products/9780596802189.EBOOK> .

        '''
        p = jlp.Processor()
        doc = '{     "#" : {            "__vocab__" : "http://www.w3.org/1999/xhtml/microdata#",           "frbr" : "http://purl.org/vocab/frbr/core#",           "dc" : "http://purl.org/dc/terms/"         },   "a" : "frbr:Work",   "@" : "<http://purl.oreilly.com/works/45U8QJGZSQKDH8N>",   "dc:title" : "Just a Geek",   "dc:creator" : "Whil Wheaton",   "frbr:realization" : ["<http://purl.oreilly.com/products/9780596007683.BOOK>", "<http://purl.oreilly.com/products/9780596802189.EBOOK>"]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'obj': u'http://purl.org/vocab/frbr/core#Work', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Whil Wheaton', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': u'http://purl.org/dc/terms/creator'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Just a Geek', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'prop': u'http://purl.org/dc/terms/title'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'obj': u'http://purl.oreilly.com/products/9780596007683.BOOK', 'prop': u'http://purl.org/vocab/frbr/core#realization'}, {'objtype': 'resource', 'subj': u'http://purl.oreilly.com/works/45U8QJGZSQKDH8N', 'obj': u'http://purl.oreilly.com/products/9780596802189.EBOOK', 'prop': u'http://purl.org/vocab/frbr/core#realization'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_5_1_to_7_examples(self):
        '''
        JSON-LD:

        {
          "foaf:homepage": "<http://manu.sporny.org>",
          "@": "<http://example.org/people#joebob>",
          "a": "<http://xmlns.com/foaf/0.1/Person>",
          "foaf:name": ["Mark Birbeck", "花澄@ja"],
          "dc:modified": "2010-05-29T14:17:39+02:00^^xsd:dateTime",
          "foaf:nick": ["stu", "groknar", "radface"]
        }

        N-Triples:
        <http://example.org/people#joebob> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/name> "Mark Birbeck" .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/name> "花澄"@ja .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/nick> "stu" .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/nick> "groknar" .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/nick> "radface" .
        <http://example.org/people#joebob> <http://xmlns.com/foaf/0.1/homepage> <http://manu.sporny.org> .
        <http://example.org/people#joebob> <http://purl.org/dc/terms/modified> "2010-05-29T14:17:39+02:00"^^<http://www.w3.org/2001/XMLSchema#dateTime> .

        '''
        p = jlp.Processor()
        doc = '{  "foaf:homepage": "<http://manu.sporny.org>",  "@": "<http://example.org/people#joebob>",  "a": "<http://xmlns.com/foaf/0.1/Person>",  "foaf:name": ["Mark Birbeck", "花澄@ja"],  "dc:modified": "2010-05-29T14:17:39+02:00^^xsd:dateTime",  "foaf:nick": ["stu", "groknar", "radface"]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'http://example.org/people#joebob', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Mark Birbeck', 'subj': u'http://example.org/people#joebob', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'lang': u'ja', 'obj': u'\u82b1\u6f84', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://xmlns.com/foaf/0.1/name', 'objtype': 'literal', 'subj': u'http://example.org/people#joebob'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'stu', 'subj': u'http://example.org/people#joebob', 'prop': u'http://xmlns.com/foaf/0.1/nick'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'groknar', 'subj': u'http://example.org/people#joebob', 'prop': u'http://xmlns.com/foaf/0.1/nick'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'radface', 'subj': u'http://example.org/people#joebob', 'prop': u'http://xmlns.com/foaf/0.1/nick'}, {'objtype': 'resource', 'subj': u'http://example.org/people#joebob', 'obj': u'http://manu.sporny.org', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'literal', 'datatype': u'http://www.w3.org/2001/XMLSchema#dateTime', 'obj': u'2010-05-29T14:17:39+02:00', 'subj': u'http://example.org/people#joebob', 'prop': u'http://purl.org/dc/terms/modified'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_5_8_example_1(self):
        '''
        JSON-LD:

        {
          "@": "<http://example.org/articles/8>",
          "dc:modified": ["2010-05-29T14:17:39+02:00^^xsd:dateTime", "2010-05-30T09:21:28-04:00^^xsd:dateTime"]
        }

        N-Triples:
        <http://example.org/articles/8> <http://purl.org/dc/terms/modified> "2010-05-29T14:17:39+02:00"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
        <http://example.org/articles/8> <http://purl.org/dc/terms/modified> "2010-05-30T09:21:28-04:00"^^<http://www.w3.org/2001/XMLSchema#dateTime> .

        '''
        p = jlp.Processor()
        doc = '{  "@": "<http://example.org/articles/8>",  "dc:modified": ["2010-05-29T14:17:39+02:00^^xsd:dateTime", "2010-05-30T09:21:28-04:00^^xsd:dateTime"]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'literal', 'datatype': u'http://www.w3.org/2001/XMLSchema#dateTime', 'obj': u'2010-05-29T14:17:39+02:00', 'subj': u'http://example.org/articles/8', 'prop': u'http://purl.org/dc/terms/modified'}, {'objtype': 'literal', 'datatype': u'http://www.w3.org/2001/XMLSchema#dateTime', 'obj': u'2010-05-30T09:21:28-04:00', 'subj': u'http://example.org/articles/8', 'prop': u'http://purl.org/dc/terms/modified'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_json_ld_spec_section_6_1_example_2(self):
        '''
        JSON-LD:

        {
          "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
          "@": 
          [
            {
              "@": "<http://example.org/people#john>",
              "a": "foaf:Person"
            },
            {
              "@": "<http://example.org/people#jane>",
              "a": "foaf:Person"
            }
          ]
        }

        N-Triples:
        <http://example.org/people#john> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        <http://example.org/people#jane> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .

        '''
        p = jlp.Processor()
        doc = '{  "#": { "foaf": "http://xmlns.com/foaf/0.1/" },  "@":   [    {      "@": "<http://example.org/people#john>",      "a": "foaf:Person"    },    {      "@": "<http://example.org/people#jane>",      "a": "foaf:Person"    }  ]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'http://example.org/people#john', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'resource', 'subj': u'http://example.org/people#jane', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_list_of_atomic_values(self):
        '''
        JSON-LD:

        [ "foo", 6.5, 34, null, true ]

        N-Triples:

        '''
        p = jlp.Processor()
        doc = '[ "foo", 6.5, 34, null, true ]'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = []
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_nested_associative_array(self):
        '''
        JSON-LD:

        {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "@": "_:bnode1",
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/bob/>",
           "foaf:name": "Bob",
           "foaf:knows": {
                            "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
                            "@": "_:bnode2",
                            "a": "foaf:Person",
                            "foaf:homepage": "<http://example.com/eve/>",
                            "foaf:name": "Eve"
                          }
        }

        N-Triples:
        _:bnode1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode1 <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:bnode2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode2 <http://xmlns.com/foaf/0.1/name> "Eve" .
        _:bnode2 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/eve/> .
        _:bnode1 <http://xmlns.com/foaf/0.1/knows> _:bnode2 .
        _:bnode1 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .

        '''
        p = jlp.Processor()
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode1",   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/bob/>",   "foaf:name": "Bob",   "foaf:knows": {                    "#": { "foaf": "http://xmlns.com/foaf/0.1/" },                    "@": "_:bnode2",                    "a": "foaf:Person",                    "foaf:homepage": "<http://example.com/eve/>",                    "foaf:name": "Eve"                  }}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Eve', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://example.com/eve/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_nested_associative_array_implicit_bnodes(self):
        '''
        JSON-LD:

        {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/bob/>",
           "foaf:name": "Bob",
           "foaf:knows": {
                            "a": "foaf:Person",
                            "foaf:homepage": "<http://example.com/eve/>",
                            "foaf:name": "Eve"
                          }
        }

        N-Triples:
        _:5ddd434833ca406ab762b83cc09f3278 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:5ddd434833ca406ab762b83cc09f3278 <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:404dfa5ddcd04fe48e9265aca28f756a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:404dfa5ddcd04fe48e9265aca28f756a <http://xmlns.com/foaf/0.1/name> "Eve" .
        _:404dfa5ddcd04fe48e9265aca28f756a <http://xmlns.com/foaf/0.1/homepage> <http://example.com/eve/> .
        _:5ddd434833ca406ab762b83cc09f3278 <http://xmlns.com/foaf/0.1/knows> _:404dfa5ddcd04fe48e9265aca28f756a .
        _:5ddd434833ca406ab762b83cc09f3278 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .

        '''
        p = jlp.Processor()
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/bob/>",   "foaf:name": "Bob",   "foaf:knows": {                    "a": "foaf:Person",                    "foaf:homepage": "<http://example.com/eve/>",                    "foaf:name": "Eve"                  }}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': '_:12a215cd56c64138bec975e91ebd90e6', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': '_:12a215cd56c64138bec975e91ebd90e6', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': '_:4548ad94b32c43fa9b1c8b90a624aa70', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Eve', 'subj': '_:4548ad94b32c43fa9b1c8b90a624aa70', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': '_:4548ad94b32c43fa9b1c8b90a624aa70', 'obj': u'http://example.com/eve/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': '_:12a215cd56c64138bec975e91ebd90e6', 'obj': '_:4548ad94b32c43fa9b1c8b90a624aa70', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'objtype': 'resource', 'subj': '_:12a215cd56c64138bec975e91ebd90e6', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_nested_associative_array_list(self):
        '''
        JSON-LD:

        {
           "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
           "@": "_:bnode1",
           "a": "foaf:Person",
           "foaf:homepage": "<http://example.com/bob/>",
           "foaf:name": "Bob",
           "foaf:knows": [ 
                            {
                              "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
                              "@": "_:bnode2",
                              "a": "foaf:Person",
                              "foaf:homepage": "<http://example.com/eve/>",
                              "foaf:name": "Eve"
                            },
                            {
                              "#": { "foaf": "http://xmlns.com/foaf/0.1/" },
                              "@": "_:bnode3",
                              "a": "foaf:Person",
                              "foaf:homepage": "<http://example.com/manu/>",
                              "foaf:name": "Manu"
                            }
                         ]
        }

        N-Triples:
        _:bnode1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode1 <http://xmlns.com/foaf/0.1/name> "Bob" .
        _:bnode2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode2 <http://xmlns.com/foaf/0.1/name> "Eve" .
        _:bnode2 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/eve/> .
        _:bnode1 <http://xmlns.com/foaf/0.1/knows> _:bnode2 .
        _:bnode3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
        _:bnode3 <http://xmlns.com/foaf/0.1/name> "Manu" .
        _:bnode3 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/manu/> .
        _:bnode1 <http://xmlns.com/foaf/0.1/knows> _:bnode3 .
        _:bnode1 <http://xmlns.com/foaf/0.1/homepage> <http://example.com/bob/> .

        '''
        p = jlp.Processor()
        doc = '{   "#": { "foaf": "http://xmlns.com/foaf/0.1/" },   "@": "_:bnode1",   "a": "foaf:Person",   "foaf:homepage": "<http://example.com/bob/>",   "foaf:name": "Bob",   "foaf:knows": [                     {                      "#": { "foaf": "http://xmlns.com/foaf/0.1/" },                      "@": "_:bnode2",                      "a": "foaf:Person",                      "foaf:homepage": "<http://example.com/eve/>",                      "foaf:name": "Eve"                    },                    {                      "#": { "foaf": "http://xmlns.com/foaf/0.1/" },                      "@": "_:bnode3",                      "a": "foaf:Person",                      "foaf:homepage": "<http://example.com/manu/>",                      "foaf:name": "Manu"                    }                 ]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Bob', 'subj': u'_:bnode1', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Eve', 'subj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode2', 'obj': u'http://example.com/eve/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'_:bnode2', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'objtype': 'resource', 'subj': u'_:bnode3', 'obj': u'http://xmlns.com/foaf/0.1/Person', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'Manu', 'subj': u'_:bnode3', 'prop': u'http://xmlns.com/foaf/0.1/name'}, {'objtype': 'resource', 'subj': u'_:bnode3', 'obj': u'http://example.com/manu/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'_:bnode3', 'prop': u'http://xmlns.com/foaf/0.1/knows'}, {'objtype': 'resource', 'subj': u'_:bnode1', 'obj': u'http://example.com/bob/', 'prop': u'http://xmlns.com/foaf/0.1/homepage'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_null(self):
        '''
        JSON-LD:

        null

        N-Triples:

        '''
        p = jlp.Processor()
        doc = 'null'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = []
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_null_as_a_key_value(self):
        '''
        JSON-LD:

        {
          "name": null
        }

        N-Triples:

        '''
        p = jlp.Processor()
        doc = '{  "name": null}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = []
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_object_with_key_value_of_list_of_atomic_values(self):
        '''
        JSON-LD:

        {
          "#": { "#vocab": "http://example.org/default/" },
          "@": "_:bnode1",
          "values": [ "foo", 6.5, 34, null, true ]
        }

        N-Triples:
        _:bnode1 <http://example.org/default/values> "foo" .
        _:bnode1 <http://example.org/default/values> "6.500000"^^<http://www.w3.org/2001/XMLSchema#float> .
        _:bnode1 <http://example.org/default/values> "34"^^<http://www.w3.org/2001/XMLSchema#integer> .
        _:bnode1 <http://example.org/default/values> "true"^^<http://www.w3.org/2001/XMLSchema#boolean> .

        '''
        p = jlp.Processor()
        doc = '{  "#": { "#vocab": "http://example.org/default/" },  "@": "_:bnode1",  "values": [ "foo", 6.5, 34, null, true ]}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'obj': u'foo', 'subj': u'_:bnode1', 'prop': u'http://example.org/default/values'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#float', 'obj': '6.500000', 'subj': u'_:bnode1', 'prop': u'http://example.org/default/values'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'obj': '34', 'subj': u'_:bnode1', 'prop': u'http://example.org/default/values'}, {'objtype': 'literal', 'datatype': 'http://www.w3.org/2001/XMLSchema#boolean', 'obj': 'true', 'subj': u'_:bnode1', 'prop': u'http://example.org/default/values'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))

    def test_relative_object_iris(self):
        '''
        JSON-LD:

        {
         "#": {"#base": "http://www.t4gm.info/concept/", "skos": "http://www.w3.org/2004/02/skos/core#"},
         "a": "skos:Concept", 
         "@": "<t4gm-4-dash-h-clubs>", 
         "skos:changeNote": "Formerly TGMI term.@en", 
         "skos:inScheme": "<http://www.t4gm.info/>",
         "skos:prefLabel": "4-H clubs@en", 
         "skos:exactMatch": "<http://id.loc.gov/vocabulary/graphicMaterials/tgm000004>", 
         "skos:broader": ["<t4gm-clubs>", "<t4gm-youth-organizations>"], 
         "skos:scopeNote": "Includes activities and structures.@en",
         "skos:altLabel": "Four-H clubs@en", 
         "skos:related": ["<t4gm-children>", "<t4gm-farmers-groups>"], 
         "skos:editorialNote": "Double index under ORGANIZATIONS&#39; FACILITIES (or NTs) for images that focus on facilities.@en"
        }

        N-Triples:
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#changeNote> "Formerly TGMI term."@en .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#inScheme> <http://www.t4gm.info/> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#prefLabel> "4-H clubs"@en .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#exactMatch> <http://id.loc.gov/vocabulary/graphicMaterials/tgm000004> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#broader> <http://www.t4gm.info/concept/t4gm-clubs> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#broader> <http://www.t4gm.info/concept/t4gm-youth-organizations> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#scopeNote> "Includes activities and structures."@en .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#altLabel> "Four-H clubs"@en .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#related> <http://www.t4gm.info/concept/t4gm-children> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#related> <http://www.t4gm.info/concept/t4gm-farmers-groups> .
        <http://www.t4gm.info/concept/t4gm-4-dash-h-clubs> <http://www.w3.org/2004/02/skos/core#editorialNote> "Double index under ORGANIZATIONS&#39; FACILITIES (or NTs) for images that focus on facilities."@en .

        '''
        p = jlp.Processor()
        doc = '{ "#": {"#base": "http://www.t4gm.info/concept/", "skos": "http://www.w3.org/2004/02/skos/core#"}, "a": "skos:Concept",  "@": "<t4gm-4-dash-h-clubs>",  "skos:changeNote": "Formerly TGMI term.@en",  "skos:inScheme": "<http://www.t4gm.info/>", "skos:prefLabel": "4-H clubs@en",  "skos:exactMatch": "<http://id.loc.gov/vocabulary/graphicMaterials/tgm000004>",  "skos:broader": ["<t4gm-clubs>", "<t4gm-youth-organizations>"],  "skos:scopeNote": "Includes activities and structures.@en", "skos:altLabel": "Four-H clubs@en",  "skos:related": ["<t4gm-children>", "<t4gm-farmers-groups>"],  "skos:editorialNote": "Double index under ORGANIZATIONS&#39; FACILITIES (or NTs) for images that focus on facilities.@en"}'
        generated_graph = [ t for t in p.triples(doc) ]
        target_graph = [{'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.w3.org/2004/02/skos/core#Concept', 'prop': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}, {'lang': u'en', 'obj': u'Formerly TGMI term.', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://www.w3.org/2004/02/skos/core#changeNote', 'objtype': 'literal', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.t4gm.info/', 'prop': u'http://www.w3.org/2004/02/skos/core#inScheme'}, {'lang': u'en', 'obj': u'4-H clubs', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://www.w3.org/2004/02/skos/core#prefLabel', 'objtype': 'literal', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://id.loc.gov/vocabulary/graphicMaterials/tgm000004', 'prop': u'http://www.w3.org/2004/02/skos/core#exactMatch'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.t4gm.info/concept/t4gm-clubs', 'prop': u'http://www.w3.org/2004/02/skos/core#broader'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.t4gm.info/concept/t4gm-youth-organizations', 'prop': u'http://www.w3.org/2004/02/skos/core#broader'}, {'lang': u'en', 'obj': u'Includes activities and structures.', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://www.w3.org/2004/02/skos/core#scopeNote', 'objtype': 'literal', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs'}, {'lang': u'en', 'obj': u'Four-H clubs', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://www.w3.org/2004/02/skos/core#altLabel', 'objtype': 'literal', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.t4gm.info/concept/t4gm-children', 'prop': u'http://www.w3.org/2004/02/skos/core#related'}, {'objtype': 'resource', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs', 'obj': u'http://www.t4gm.info/concept/t4gm-farmers-groups', 'prop': u'http://www.w3.org/2004/02/skos/core#related'}, {'lang': u'en', 'obj': u'Double index under ORGANIZATIONS&#39; FACILITIES (or NTs) for images that focus on facilities.', 'datatype': 'http://www.w3.org/2001/XMLSchema#string', 'prop': u'http://www.w3.org/2004/02/skos/core#editorialNote', 'objtype': 'literal', 'subj': u'http://www.t4gm.info/concept/t4gm-4-dash-h-clubs'}]
        self.assertTrue(graph_equal(target_graph, generated_graph))


if __name__ == "__main__":
    unittest.main()
