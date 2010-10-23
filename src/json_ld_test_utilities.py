# -*- coding: utf-8 -*-
'''
Created on Oct 18, 2010

@author: ballen
'''

import re

def triple_in_graph(triple, graph):
    '''
    Returns True if a triple matches a triple in a graph (i.e., list of triples).
    '''
    bnode_pattern = re.compile("^_\:\w+$")
    s = triple['subj']
    p = triple['prop']
    o = triple['obj']            
    for t in graph:
        subj_bnode = (bnode_pattern.match(s) and bnode_pattern.match(t['subj']))
        obj_bnode = (bnode_pattern.match(o) and bnode_pattern.match(t['obj']))
        subj_eq = (s == t['subj'])
        obj_eq = (o == t['obj'])
        subj_match = (subj_bnode or subj_eq)
        prop_match = (p == t['prop'])
        obj_match = (obj_bnode or obj_eq)
        if subj_match and prop_match and obj_match:
            return True
    return False
        
def graph_equal(graph1, graph2):
    '''
    Returns True if two graphs (i.e., lists of triples) are equivalent.
            
    Two graphs are equivalent iff they have the same number of triples and each triple 
    in one graph matches a triple in the other.
    '''
    if len(graph1) != len(graph2):
        return False
    for triple in graph1:
        if not triple_in_graph(triple, graph2):
            return False
    return True

        
