'''
Created on Sep 6, 2012

@author: tulvur
'''
from abc import abstractmethod, ABCMeta
import json
import bson
from dict2xml import dict2xml


class Clue(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    
    # constant for the id of the clue class
    @staticmethod
    def ID_P():
        return "i"
    
    @staticmethod
    def ID():
        '''Returns the id of the current type of clue'''
        raise NotImplementedError('Pseudo abstract identifier')
        
    @abstractmethod
    def _toDictionary(self):
        pass
    
    @abstractmethod
    def _fromDictionary(self, diction):
        pass
    
    def toJson(self):
        return json.dumps(self._toDictionary())
    
    def parseJson(self, json_str):
        diction = json.loads(json_str)
        self._fromDictionary(diction)
    
    def toBson(self): # but BSON is longer than JSON in many cases
        return bson.dumps({'b':self._toDictionary()}) # key-value needed (the list cannot be serialized as is
    
    def toXML(self):
        return dict2xml(self._toDictionary())
    
    def _extractNamespaces(self, graph):
        schemas = []
        
        # Is call just to ensure that automatic binding is performed.
        # TODO find a better alternative of forcing automatic binding!
        graph.serialize(format='n3')
        
        # WARNING:
        #    The iteration works well in different ways for:
        #       + rdflib.Graph: where we should use graph.namespace_manager.namespaces()
        #       + rdflib.Graph.Graph: The one used in dataaccess layer, where we use graph.namespaces()
        for pref in graph.namespaces():
            if not pref[1].startswith('file://'):
                schemas.append(pref)
        return schemas
    
    @abstractmethod
    def isCandidate(self, template):
        pass