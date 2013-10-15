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

from rdflib import URIRef
from rdflib import Graph
from rdflib import RDF
from rdflib import RDFS
from rdflib.Literal import _XSD_NS as XSD_NS
from rdflib import Namespace # for OWL namespace... :-S

from clueseval.clues.parent_clue import Clue


class SchemaBasedClue(Clue):
    
    # constant for prefix
    @staticmethod
    def _SCHEMA():
        return "s"
    
    @staticmethod
    def ID():
        return 0
    
    def __init__(self):
        super(SchemaBasedClue, self).__init__()
        self._schemas = set()
    
    @property
    def schemas(self):
        return self._schemas
    
    @schemas.setter
    def schemas(self, schemas):
        self._schemas = set(schemas)
    
    def parseFile(self, filename):
        self.parseGraph( Graph().parse(filename, format="n3") )
    
    def parseGraph(self, graph):
        OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
        XML_NS = Namespace("http://www.w3.org/XML/1998/namespace")
        unfiltered = self._extractNamespaces(graph)
        for _, uri in unfiltered:
            if uri not in (RDF.RDFNS, RDFS.RDFSNS, OWL_NS, XSD_NS, XML_NS):
                self._schemas.add(uri) # self._schemas.append((name, uri)) # we do not need the names of the prefixes too
    
    def _fromDictionary(self, diction):
        self._schemas = set()
        if isinstance(diction, (list, tuple)):
            for el in diction:
                self._schemas.add(URIRef(el))
        else: raise Exception('Unexpected json content.')
    
    def _toDictionary(self):
        return [str(t) for t in self._schemas]
    
    def isCandidate(self, template):
        for part in template:
            if part is not None:
                for sch in self._schemas:
                    if sch not in (RDF.RDFNS, RDFS.RDFSNS):
                        if str(part).startswith(str(sch)):
                            return True
        return False
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._schemas==other._schemas
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == '__main__':
    gossip = SchemaBasedClue()
    gossip.parseFile('../../../files/7CAMPA_measures.n3')
    print gossip.toJson()