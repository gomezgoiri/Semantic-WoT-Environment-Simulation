'''
Created on Aug 3, 2012

@author: tulvur
'''
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF
from rdflib import RDFS

from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue


class PredicateBasedClue(Clue):    
    # constant for predicate
    @staticmethod
    def _PREDICATE():
        return "p"
    
    @staticmethod
    def ID():
        return 1
    
    def __init__(self):
        Clue.__init__(self)
        self._schemas = set()
        self._predicates = set()
    
    @property
    def schemas(self):
        return self._schemas
    
    @schemas.setter
    def schemas(self, schemas):
        self._schemas = set(schemas)
        
    @property
    def predicates(self):
        return self._predicates
    
    @predicates.setter
    def predicates(self, predicates):
        self._predicates = set(predicates)
    
    def parseFile(self, filename):
        self.parseGraph( Graph().parse(filename, format="n3") )
    
    def parseGraph(self, graph):
        self._schemas = set(self._extractNamespaces(graph))
        self._predicates = set(self._extractPredicates(graph))
    
    def _extractPredicates(self, graph):
        ret = set()
        for t in graph.triples((None, None, None)):
            if not t[1].startswith(str(RDF.RDFNS)) and not t[1].startswith(str(RDFS.RDFSNS)):
                ret.add(t[1])
        return ret
    
    def _fromDictionary(self, diction):
        self._schemas = [(name, URIRef(uri)) for name, uri in diction[SchemaBasedClue._SCHEMA()]]
        for prf_name, prf_uri in self._schemas:
            for uris_endings in diction[PredicateBasedClue._PREDICATE()][prf_name]:
                self._predicates.add(URIRef(prf_uri + uris_endings)) # cause the URI is passed as a string
    
    def _toDictionary(self):
        diction = {}
        diction[SchemaBasedClue._SCHEMA()] = []
        diction[PredicateBasedClue._PREDICATE()] = {}
        
        for t in self._predicates:
            for p in self._schemas:
                if t.startswith(p[1]):
                    prf_name = str(p[0])
                    prf_uri = str(p[1])
                    if prf_name not in diction[PredicateBasedClue._PREDICATE()]:
                        diction[PredicateBasedClue._PREDICATE()][prf_name] = []
                        diction[SchemaBasedClue._SCHEMA()].append((prf_name, prf_uri)) # it can be reduced by reducing the name of the prefixes
                        
                    uri_to_shorten = str(t).replace(prf_uri, '')
                    diction[PredicateBasedClue._PREDICATE()][prf_name].append(uri_to_shorten)
                    break
        
        return diction # otherwise set cannot be converted to json
    
    def isCandidate(self, template):
        if template[1] is not None:
            for pred in self._predicates:
                if template[1]==pred:
                    return True
        return False
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._schemas==other._schemas:
                if self._predicates==other._predicates:
                    return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == '__main__':
    c1 = PredicateBasedClue()
    c1.parseFile("../../../files/XSCA3_2003_4_6.n3")
    
    json_str = c1.toJson()
    print json_str
    
    c2 = PredicateBasedClue()
    c2.parseJson(json_str)
    
    #print g2.schemas
    print c2.predicates