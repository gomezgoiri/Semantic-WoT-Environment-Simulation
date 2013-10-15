# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import unittest
from rdflib import Namespace
from netuse.triplespace.caching.queries import QueryCacher
from netuse.triplespace.network.httpelements import HttpResponse


class FakeNode(object):
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __eq__(self, other):
        return self.id == other.id and self.name == other.name
    
    def __str__(self):
        return self.name


ns_test = Namespace("http://www.morelab.deusto.es/test#")

class TestQueryCacher(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.template1 = ( ns_test.subj1, ns_test.pred1, ns_test.obj1)
        self.template2 = ( ns_test.subj2, None, None)
        self.template3 = ( ns_test.subj3, ns_test.pred1, ns_test.obj1)
        
        self.cache = QueryCacher()
        self.cache.positive_answers = { self.template1: set(["node1", "node2"]),
                                        self.template2: set(["node1_t2", "node2_t2"]) }
        self.cache.negative_answers = { self.template1: set(["node3", "node4", "node5"]),
                                        self.template2: set(["node3_t2", "node4_t2", "node5_t2"]) }
    
    def test_get_relevant_nodes(self):
        nodes = [ FakeNode(8, "node8"), # unknown
                  FakeNode(1, "node1"), # positive response in the past
                  FakeNode(9, "node9"), # unknown
                  FakeNode(3, "node3") ] # negative response in the past
        
        relevant = self.cache.get_relevant_nodes( self.template1, nodes )
        self.assertEquals( set([ nodes[0], nodes[1], nodes[2] ]), relevant )
        
        relevant = self.cache.get_relevant_nodes( self.template2, nodes )
        self.assertEquals( set(nodes), relevant )

    def test_cache_positive(self):
        self.cache.cache( self.template1,
                          FakeNode(10, "node10"),
                          HttpResponse(3, "blah", status=200) )
        self.assertEquals( 3, len(self.cache.positive_answers[self.template1]) )
        self.assertEquals( 3, len(self.cache.negative_answers[self.template1]) )
        self.assertTrue( "node10" in self.cache.positive_answers[self.template1] )
        self.assertEquals( 2, len(self.cache.positive_answers[self.template2]) )
        
    def test_cache_negative(self):
        self.cache.cache( self.template1,
                          FakeNode(11, "node11"),
                          HttpResponse(3, "blah", status=404) )
        
        self.assertEquals( 2, len(self.cache.positive_answers[self.template1]) )        
        self.assertEquals( 4, len(self.cache.negative_answers[self.template1]) )
        self.assertTrue( "node11" in self.cache.negative_answers[self.template1] )
        self.assertEquals( 3, len(self.cache.negative_answers[self.template2]) )  
        
    def test_cache_negative_former_positive(self):
        self.cache.cache( self.template1,
                          FakeNode(2, "node2"),
                          HttpResponse(3, "blah", status=404) )
        
        self.assertEquals( 1, len(self.cache.positive_answers[self.template1]) )
        self.assertFalse( "node2" in self.cache.positive_answers[self.template1] )
        self.assertEquals( 2, len(self.cache.positive_answers[self.template2]) )
        
        self.assertEquals( 4, len(self.cache.negative_answers[self.template1]) )
        self.assertTrue( "node2" in self.cache.negative_answers[self.template1] )
        self.assertEquals( 3, len(self.cache.negative_answers[self.template2]) )
    
    def test_cache_positive_former_negative(self):
        self.cache.cache( self.template1,
                          FakeNode(5, "node5"),
                          HttpResponse(3, "blah", status=200) )
        
        self.assertEquals( 3, len(self.cache.positive_answers[self.template1]) )
        self.assertTrue( "node5" in self.cache.positive_answers[self.template1] )
        self.assertEquals( 2, len(self.cache.positive_answers[self.template2]) )
        
        self.assertEquals( 2, len(self.cache.negative_answers[self.template1]) )
        self.assertFalse( "node5" in self.cache.negative_answers[self.template1] )
        self.assertEquals( 3, len(self.cache.negative_answers[self.template2]) )

if __name__ == '__main__':
    unittest.main()