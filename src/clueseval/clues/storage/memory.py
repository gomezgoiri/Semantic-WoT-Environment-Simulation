'''
Created on Oct 26, 2012

@author: tulvur
'''

from clueseval.clues.storage.abstract_store import AbstractStore, AggregationClueUtils
from clueseval.clues.parent_clue import Clue
from clueseval.clues.node_attached import ClueWithNode
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue

def compare_expiry(tuple_a, tuple_b):
        return cmp(int(tuple_a[0]), int(tuple_b[0])) # compare as integers


class MemoryClueStore(AbstractStore):
    
    def __init__(self, tipe=None):
        self.bynode = {}
        self.type = tipe
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    # return the nodes which may have relevant data for a given query
    def get_query_candidates(self, template):
        candidates = set()
        for node_name, clue in self.bynode.iteritems():
            if clue.isCandidate(template):
                candidates.add(node_name)
        return candidates
    
    def _create_temporary_dictionaries(self):
        tmpDictios = {}
        for node, c in self.bynode.iteritems():
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
    
    def toJson(self):
        dictio = {}
        dictio[Clue.ID_P()] = self.type
        
        if self.type==SchemaBasedClue.ID():
            dictio[SchemaBasedClue._SCHEMA()] = {}
            for node, c in self.bynode.iteritems():
                dictio[SchemaBasedClue._SCHEMA()][node] = c._toDictionary()
        elif self.type==PredicateBasedClue.ID():
            tmpDictios = self._create_temporary_dictionaries()
            
            dictio[SchemaBasedClue._SCHEMA()] = self._gather_schemas(tmpDictios.itervalues())
            dictio[PredicateBasedClue._PREDICATE()] = self._gather_shortened_uris_by_node(tmpDictios.iteritems(), PredicateBasedClue._PREDICATE())
        elif self.type==PredicateBasedClue.ID():
            tmpDictios = self._create_temporary_dictionaries()
            
            dictio[SchemaBasedClue._SCHEMA()] = self._gather_schemas(tmpDictios.itervalues())
            dictio[ClassBasedClue._CLASS()] = self._gather_shortened_uris_by_node(tmpDictios.iteritems(), ClassBasedClue._CLASS())
                    
        return AggregationClueUtils.toJson(dictio)
    
    def _divide_clue(self, all_schemas, short_uris_based_clue):
        disgregated_clue = {}
        disgregated_clue[SchemaBasedClue._SCHEMA()] = all_schemas
        disgregated_clue[PredicateBasedClue._PREDICATE()] = short_uris_based_clue
        
        return disgregated_clue
    
    # Overrides previously stored clues
    def fromJson(self, json_txt):
        dictio = AggregationClueUtils.fromJson(json_txt)
        self.type = dictio[Clue.ID_P()]
        self.bynode = {}
        
        if self.type==SchemaBasedClue.ID():
            for node, clue in dictio[SchemaBasedClue._SCHEMA()].iteritems():
                c = SchemaBasedClue()
                c._fromDictionary(clue)
                self.bynode[node] = c
        elif self.type==PredicateBasedClue.ID():
            all_schemas = dictio[SchemaBasedClue._SCHEMA()]
            for node, clue in dictio[PredicateBasedClue._PREDICATE()].iteritems():                 
                c = PredicateBasedClue()
                c._fromDictionary( self._divide_clue(all_schemas, clue) )
                self.bynode[node] = c
        elif self.type==PredicateBasedClue.ID():
            all_schemas = dictio[SchemaBasedClue._SCHEMA()]
            for node, clue in dictio[ClassBasedClue._CLASS()].iteritems():                 
                c = PredicateBasedClue()
                c._fromDictionary( self._divide_clue(all_schemas, clue) )
                self.bynode[node] = c
    
    
    def add_clue(self, node_name, clue_json):
        cwn = ClueWithNode() # TODO it should specify just the type
        cwn.parseJson(clue_json)
        
        clue_type = cwn.clue.ID()
        if self.type==None: # If this is the first clue, it define the type of store
            self.type = clue_type
        else:
            if clue_type is not self.type:
                raise Exception("This store only accepts clues of the type %d"%(self.type))
            
        self.bynode[node_name] = cwn.clue