'''
Created on May 23, 2013

@author: tulvur
'''

import unittest
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


class TestQueryCacher(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.cache = QueryCacher()
        self.cache.positive_answers = set(["node1", "node2"])
        self.cache.negative_answers = set(["node3", "node4", "node5"])
    
    def test_get_relevant_nodes(self):
        nodes = [ FakeNode(8, "node8"), # unknown
                  FakeNode(1, "node1"), # positive response in the past
                  FakeNode(9, "node9"), # unknown
                  FakeNode(3, "node3") ] # negative response in the past
        
        relevant = self.cache.get_relevant_nodes( nodes )
        self.assertEquals( set([ nodes[0], nodes[1], nodes[2] ]), relevant )

    def test_cache_positive(self):
        self.cache.cache( FakeNode(10, "node10"), HttpResponse(3, "blah", status=200) )
        self.assertEquals( 3, len(self.cache.positive_answers) )
        self.assertEquals( 3, len(self.cache.negative_answers) )
        self.assertTrue( "node10" in self.cache.positive_answers )
        
    def test_cache_negative(self):
        self.cache.cache( FakeNode(11, "node11"), HttpResponse(3, "blah", status=404) )
        self.assertEquals( 2, len(self.cache.positive_answers) )
        self.assertEquals( 4, len(self.cache.negative_answers) )
        self.assertTrue( "node11" in self.cache.negative_answers )
        
    def test_cache_negative_former_positive(self):
        self.cache.cache( FakeNode(2, "node2"), HttpResponse(3, "blah", status=404) )
        self.assertEquals( 1, len(self.cache.positive_answers) )
        self.assertFalse( "node2" in self.cache.positive_answers )
        self.assertEquals( 4, len(self.cache.negative_answers) )
        self.assertTrue( "node2" in self.cache.negative_answers )
    
    def test_cache_positive_former_negative(self):
        self.cache.cache( FakeNode(5, "node5"), HttpResponse(3, "blah", status=200) )
        self.assertEquals( 3, len(self.cache.positive_answers) )
        self.assertTrue( "node5" in self.cache.positive_answers )
        self.assertEquals( 2, len(self.cache.negative_answers) )
        self.assertFalse( "node5" in self.cache.negative_answers )

if __name__ == '__main__':
    unittest.main()