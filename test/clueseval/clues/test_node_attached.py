'''
Created on Sep 10, 2012

@author: tulvur
'''
import unittest
from rdflib import URIRef
from clueseval.clues.node_attached import ClueWithNode
from clueseval.clues.predicate_based import PredicateBasedClue

class TestStats(unittest.TestCase):
    
    def setUp(self):
        self.base_clue = PredicateBasedClue()
        self.base_clue.schemas = [('deusto', URIRef('http://deusto.es/')), ('meneame',URIRef('http://meneame.net#'))]
        self.base_clue.predicates = [URIRef('http://deusto.es/mola'),URIRef('http://meneame.net#chachi'),URIRef('http://deusto.es/guay')]
        
        self.clue = ClueWithNode('node1', self.base_clue)
    
    def test_parseJson_toJson(self):
        clue2 = ClueWithNode()
        clue2.parseJson(self.clue.toJson())
        
        self.assertEquals(self.clue.node, clue2.node)
        
        for name, uri in self.clue.clue.schemas:
            self.assertTrue((name,uri) in clue2.clue.schemas)
            
        for p in self.clue.clue.predicates:
            self.assertTrue(p in clue2.clue.predicates)

       
if __name__ == '__main__':
    unittest.main()
    