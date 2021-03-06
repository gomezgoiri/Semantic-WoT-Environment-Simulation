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

from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue


class ClueWithNode(Clue):
      
    # constant for node
    @staticmethod
    def NODE():
        return "n"
    
    # constant for clue
    @staticmethod
    def CLUE():
        return "c"
    
    @staticmethod
    def ID():
        return 3
    
    def __init__(self, node=None, clue=None):
        '''The name (or IP) of the node containing the clue.'''
        super(ClueWithNode, self).__init__()
        self.node = node
        self.clue = clue
        
    def _toDictionary(self):
        ret = {}
        ret[ClueWithNode.NODE()] = self.node
        ret[Clue.ID_P()] = self.clue.ID()
        ret[ClueWithNode.CLUE()] = self.clue._toDictionary()
        return ret
            
    def _fromDictionary(self, parsed):
        self.node = parsed[ClueWithNode.NODE()]
        
        idp = parsed[Clue.ID_P()]
        if idp==SchemaBasedClue.ID():
            self.clue = SchemaBasedClue()
        elif idp==PredicateBasedClue.ID():
            self.clue = PredicateBasedClue()
        elif idp==ClassBasedClue.ID():
            self.clue = ClassBasedClue()
        
        self.clue._fromDictionary(parsed[ClueWithNode.CLUE()])
        
    def isCandidate(self, template):
        return self.clue.isCandidate(template)
        
if __name__ == '__main__':
    clue = SchemaBasedClue()
    clue.parseFile('../../../files/XSCA3_2003_4_6.n3')
    
    clueWN = ClueWithNode('pepito', clue)
    print clueWN.toJson()
    
    clueWN2 = ClueWithNode()
    clueWN2.parseJson(clueWN.toJson())
    print clueWN2.toJson()