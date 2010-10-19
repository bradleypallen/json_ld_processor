#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from json_ld_to_ntriples import json_ld_to_ntriples
from json_ld_to_unittest import json_ld_to_unittest

print "#!/usr/bin/python"
print "# -*- coding: utf-8 -*-"
print
print "import unittest, json_ld_processor as jlp"
print "from json_ld_test_utilities import graph_equal"
print
print "class TestProcessor(unittest.TestCase):"
print "    '''"
print "    Defines a unittest test processor for automated unit testing of the JSON-LD processor."
print "    Tests are largely drawn from examples in the specification at http://json-ld.org/spec/latest/,"
print "    but also include some based on individual and group conversations."
print
print "    Each test case simply takes a JSON-LD document, deserializes it using triples(),"
print "    and asserts that the generated list of triples is the same as a target list of triples."
print "    '''"
print
for path, dirlist, filelist in os.walk('../test/'):
    for name in filelist:
        if name.split(".")[1] == 'json':
            case = name.split(".")[0]
            filename = os.path.join(path, name)
            file = open(filename, 'r')
            doc = file.read()
            json_ld_to_unittest(case, doc)
print
print
print 'if __name__ == "__main__":'
print "    unittest.main()"