'''
Created on Oct 26, 2012

@author: tulvur
'''
import json
from abc import abstractmethod, ABCMeta
from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue

class AggregationClueUtils(object):
    """
    {
      "i": 1,
      "s": [
        ["dc", "http://purl.org/dc/elements/1.1/"],
        ["dul", "http://www.loa.istc.cnr.it/ontologies/DUL.owl#"],
        ["ssn", "http://purl.oclc.org/NET/ssnx/ssn#"]
          ],
      "p": {
        "node1": {
          "ssn": ["observedBy", "observationResult"],
          "dul": ["isClassifiedBy"]
        },
        "node0": {
          "ssn": ["observes"],
          "dc": ["description"]
    } } }
    """
    
    @staticmethod
    def validate(dictionary):
        if Clue.ID_P() in dictionary:
            if dictionary[Clue.ID_P()] is SchemaBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary
            elif dictionary[Clue.ID_P()] is PredicateBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary and PredicateBasedClue._PREDICATE() in dictionary
            elif dictionary[Clue.ID_P()] is ClassBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary and ClassBasedClue._CLASS() in dictionary
        return False
    
    @staticmethod
    def toJson(dictionary):
        if not AggregationClueUtils.validate(dictionary):
            raise Exception("Malformed clue.")
        return json.dumps(dictionary)
    
    @staticmethod
    def fromJson(json_str):
        dictionary = json.loads(json_str)
        if not AggregationClueUtils.validate(dictionary):
            raise Exception("Malformed clue.")
        return dictionary


class AbstractStore(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
        
    @abstractmethod
    def add_clue(self, node_name, clue_json):
        pass
    
    @abstractmethod
    def toJson(self):
        pass
    
    @abstractmethod
    def fromJson(self, json_str):
        pass
    
    @abstractmethod
    def get_query_candidates(self, template):
        pass