'''
Created on Sep 10, 2012

@author: tulvur
'''
import json
from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue


class ClueAggregation(object):
    
    NODE_FIELD = 0
    CLUE_FIELD = 1 
    
    def __init__(self, clues=None):
        '''Clues is a list of tuples which contain the following fields:
             0. the name (IP) of the node containing the clue
             1. the clue sent by that node
             Note that all the clues should be of the same type.
         '''
        self.clues = clues
        self.type = -1 if clues==None or not clues else clues[0][ClueAggregation.CLUE_FIELD].ID() # the type of the first element
    
    def _create_temporary_dictionaries(self):
        tmpDictios = {}
        for node, c in self.clues:
            tmpDictios[node] = c._toDictionary()
        return tmpDictios
    
    def _gather_schemas(self, iter_dictio):
        ret = set()
        for tdict in iter_dictio:
            ret.update(tdict[SchemaBasedClue._SCHEMA()])
            # or ret = ret.union(tdict[SchemaBasedClue._SCHEMA()])
        return list(ret)
        
    def _gather_shortened_uris_by_node(self, iter_node_tdict, key_name):
        ret = {}
        for node, tdict in iter_node_tdict:
            ret[node] = tdict[key_name]
        return ret
    
    def _toDictionary(self):
        dictio = {}
        dictio[Clue.ID_P()] = self.type
        
        if self.type==SchemaBasedClue.ID():
            dictio[SchemaBasedClue._SCHEMA()] = {}
            for node, c in self.clues:
                dictio[SchemaBasedClue._SCHEMA()][node] = c._toDictionary()
        elif self.type==PredicateBasedClue.ID():
            tmpDictios = self._create_temporary_dictionaries()
            
            dictio[SchemaBasedClue._SCHEMA()] = self._gather_schemas(tmpDictios.itervalues())
            dictio[PredicateBasedClue._PREDICATE()] = self._gather_shortened_uris_by_node(tmpDictios.iteritems(), PredicateBasedClue._PREDICATE())
        elif self.type==PredicateBasedClue.ID():
            tmpDictios = self._create_temporary_dictionaries()
            
            dictio[SchemaBasedClue._SCHEMA()] = self._gather_schemas(tmpDictios.itervalues())
            dictio[ClassBasedClue._CLASS()] = self._gather_shortened_uris_by_node(tmpDictios.iteritems(), ClassBasedClue._CLASS())
                    
        return dictio
    
    def _divide_clue(self, all_schemas, short_uris_based_clue):
        disgregated_clue = {}
        disgregated_clue[SchemaBasedClue._SCHEMA()] = all_schemas
        disgregated_clue[PredicateBasedClue._PREDICATE()] = short_uris_based_clue
        
        return disgregated_clue
    
    def _fromDictionary(self, dictio):
        self.type = dictio[Clue.ID_P()]
        self.clues = []
        
        if self.type==SchemaBasedClue.ID():
            for node, clue in dictio[SchemaBasedClue._SCHEMA()].iteritems():
                c = SchemaBasedClue()
                c._fromDictionary(clue)
                self.clues.append((node,c))
        elif self.type==PredicateBasedClue.ID():
            all_schemas = dictio[SchemaBasedClue._SCHEMA()]
            for node, clue in dictio[PredicateBasedClue._PREDICATE()].iteritems():                 
                c = PredicateBasedClue()
                c._fromDictionary( self._divide_clue(all_schemas, clue) )
                self.clues.append((node,c))
        elif self.type==PredicateBasedClue.ID():
            all_schemas = dictio[SchemaBasedClue._SCHEMA()]
            for node, clue in dictio[ClassBasedClue._CLASS()].iteritems():                 
                c = PredicateBasedClue()
                c._fromDictionary( self._divide_clue(all_schemas, clue) )
                self.clues.append((node,c))
    
    def toJson(self):
        return json.dumps(self._toDictionary())
    
    def fromJson(self, json_str):
        diction = json.loads(json_str)
        self._fromDictionary(diction)