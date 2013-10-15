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

from rdflib import Graph
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import RDFS

from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.DLP.DLNormalization import NormalFormReduction
from FuXi.Horn.HornRules import HornFromN3

from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue


class ClassBasedClue(Clue):
    
    # constant for class
    @staticmethod
    def _CLASS():
        return "c"
    
    @staticmethod
    def ID():
        return 2
    
    def __init__(self, tbox):
        super(ClassBasedClue, self).__init__()
        self._schemas = set()
        self._classes = set()
        self.tbox = tbox
        
    @property
    def schemas(self):
        return self._schemas
    
    @schemas.setter
    def schemas(self, schemas):
        self._schemas = set(schemas)
        
    @property
    def classes(self):
        return self._classes
    
    @classes.setter
    def classes(self, classes):
        self._classes = set(classes)

    def parseFile(self, filename):
        graph = Graph().parse(filename, format="n3")
        self.parseGraph(graph)
    
    def parseGraph(self, graph):
        self._schemas = self._extractNamespaces(graph)
        self._classes = self._extractRdfTypes(graph)
    
    def _extractRdfTypes(self, graph):
        ret = set()
        for t in graph.triples((None, RDF.type, None)): # return a Gossiped piece of info from own Graph
            if not isinstance(t[2], BNode): # to avoid blank nodes
                ret.add(t[2])
        return ret
    
    def _fromDictionary(self, diction): # TODO refactor: exactly the same as in predicate_based
        self._schemas = set( [(name, URIRef(value)) for name, value in diction[SchemaBasedClue._SCHEMA()]] )
        for prf_name, prf_uri in self._schemas:
            for uris_endings in diction[ClassBasedClue._CLASS()][prf_name]:
                self._classes.add(URIRef(prf_uri + uris_endings)) # cause the URI is passed as a string
    
    def _toDictionary(self): # TODO refactor: very similar to predicate_based
        diction = {}
        diction[SchemaBasedClue._SCHEMA()] = []
        diction[ClassBasedClue._CLASS()] = {}
        
        # to check first longest URIs (think on prefA='http://uri1' prefB='http://uri1/uri2/df/')
        sorted_schemas = sorted(self._schemas, key=lambda x: len(x[1]), reverse=True)
        for t in self._classes:
            for p in sorted_schemas:
                if t.startswith(p[1]):
                    prf_name = str(p[0])
                    prf_uri = str(p[1])
                    if prf_name not in diction[ClassBasedClue._CLASS()]:
                        diction[ClassBasedClue._CLASS()][prf_name] = []
                        diction[SchemaBasedClue._SCHEMA()].append((prf_name, prf_uri)) # it can be reduced by reducing the name of the prefixes
                        
                    uri_to_shorten = str(t).replace(prf_uri, '')
                    diction[ClassBasedClue._CLASS()][prf_name].append(uri_to_shorten)
                    break
        
        return diction # otherwise set cannot be converted to json
        
    def isCandidate(self, template):
        """ Tests if according to this gossiped piece of information
            the node which have it is candidate to answer a query or not """
        if template[1]!=None:
            if template[1]==RDF.type and template[2]!=None:
                return self.__hasClassesFromThisType(self.tbox, template[2])
            else: return self.__doesPredicateBelongToClass(self.tbox, template[1])
        elif template[2]!=None:
            return template[2] in self._classes
        else: return True # we cannot predict anything with a subject or an object
            
    def __hasClassesFromThisType(self, ontology, rdftype):
        if rdftype in self._classes:
            return True
        return False
        # already done if it was expanded
        #for subtype, _, _ in ontology.triples((None, RDFS.subClassOf, rdftype)):
        #    if subtype in self._classes:
        #        return True
        
    def __hasClassesOfRange(self, ontology, predicate, rdftype):
        for _,_,_ in ontology.triples((predicate,RDFS.range,rdftype)):
            return True # has at least one element which matches the template
        return False
    
    def __hasClassesOfDomain(self, ontology, predicate, rdftype):
        for _,_,_ in ontology.triples((predicate,RDFS.domain,rdftype)):
            return True
        # already done if it was expanded
        #for _,_,o in ontology.triples((predicate,RDFS.domain,None)):
        #    for _,_,_ in ontology.triples((rdftype,RDFS.subClassOf,o)):
        #        return True # has at least one element which matches the template
        return False
    
    def __doesPredicateBelongToClass(self, ontology, predicate):
        """ is subject of a rdf:type? """
        dom = False
        #ran = False
        for t in self._classes:
            dom = dom or self.__hasClassesOfDomain(ontology, predicate, t)
            #ran = dom or self.__hasClassesOfRange(ontology, predicate, t)
            # with "AND" could be quite restrictive, we may have classes which whose type we don't know (because we don't infer anything)
            if dom: return True
        return False
    
    def isEmpty(self):
        return not self._classes and not self.subclass and not self.subproperty
        
        #if template[0]!=None:
        #    isSubjectInstanceOfClass(template[0])
        # is predicate of rdf:type?
        # object?
        
    def expand(self):
        abox = Graph()
        i = 0
        for t in self._classes:
            abox.add( (URIRef("http://el%i"%(i)), RDF.type, t) )
            i += 1
        
        _, _, network = SetupRuleStore(makeNetwork=True)
        NormalFormReduction(self.tbox)
        
        # Warning: The use of pD-rules is a memory killer!
        for rule in HornFromN3('http://www.agfa.com/w3c/euler/rdfs-rules.n3'): #'../lib/python-dlp/fuxi/test/pD-rules.n3'): #HornFromDL(self.tBoxGraph):
            network.buildNetworkFromClause(rule)
        network.feedFactsToAdd(generateTokenSet(self.tbox))
        network.feedFactsToAdd(generateTokenSet(abox))
        
        self._classes = self._classes.union( self._extractRdfTypes(network.inferredFacts) )

if __name__ == '__main__':
    
    tbox = Graph().parse("../../../files/Ssn.owl")
    tbox.parse("../../../files/sensor-observation.owl")
    
    c1 = ClassBasedClue(tbox)
    c1.parseFile("../../../files/7CAMPA_measures.n3")
    
    print c1.toJson()
    
    c1.expand()
    
    json_str = c1.toJson()
    print json_str
    
    c2 = ClassBasedClue(None)
    c2.parseJson(json_str)
    
    print c2.classes
    print c2.schemas