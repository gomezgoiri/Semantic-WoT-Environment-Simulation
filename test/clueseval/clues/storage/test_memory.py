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
from rdflib import URIRef
from clueseval.clues.node_attached import ClueWithNode
from clueseval.clues.storage.memory import MemoryClueStore
from clueseval.clues.predicate_based import PredicateBasedClue


# TODO test aggregations of schema-based and class-based clues
class TestClueAggregation(unittest.TestCase):
    
    def setUp(self):
        self.clue_store = MemoryClueStore()
        self.clue_store.start()
        
        clue = PredicateBasedClue()
        clue.schemas = [('ssn', URIRef('http://purl.oclc.org/NET/ssnx/ssn#')), ('dc',URIRef('http://purl.org/dc/elements/1.1/'))]
        clue.predicates = [URIRef('http://purl.oclc.org/NET/ssnx/ssn#observes'), URIRef('http://purl.org/dc/elements/1.1/description')]
        self.clue_store.add_clue('node0', ClueWithNode('XXX', clue).toJson())
        
        clue = PredicateBasedClue()
        clue.schemas = [('ssn', URIRef('http://purl.oclc.org/NET/ssnx/ssn#')), ('dul',URIRef('http://www.loa.istc.cnr.it/ontologies/DUL.owl#'))]
        clue.predicates = [URIRef('http://purl.oclc.org/NET/ssnx/ssn#observedBy'), URIRef('http://purl.oclc.org/NET/ssnx/ssn#observationResult'), URIRef('http://www.loa.istc.cnr.it/ontologies/DUL.owl#isClassifiedBy')]
        self.clue_store.add_clue('node1', ClueWithNode('XXX', clue).toJson())
        
    def tearDown(self):
        self.clue_store.stop()
        
    def _assert_predicate_in_original_clues(self, node, parsed_clue, original_clue):
        # if not optimized, parsed may contain more schemas than really used in that clue
        # In other words, all original clues' schemas exist in parsed clues, but not viceversa.
        for sch in original_clue.schemas:
            self.assertTrue(sch in parsed_clue.schemas)
        
        for predicate in parsed_clue.predicates:
            self.assertTrue(predicate in original_clue.predicates)
    
    def test_parseJson_predicates(self):
        clue_store2 = MemoryClueStore()
        clue_store2.start()
        
        try:
            clue_store2.fromJson(self.clue_store.toJson())
            
            self.assertEquals(self.clue_store.type, clue_store2.type)
            
            for node, cl in clue_store2.bynode.iteritems():
                self.assertTrue(node in self.clue_store.bynode)
                self._assert_predicate_in_original_clues(node, cl, self.clue_store.bynode[node])
        finally:
            clue_store2.stop()


if __name__ == '__main__':
    unittest.main()
    