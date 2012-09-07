'''
Created on Feb 6, 2012

@author: tulvur
'''
import json
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import RDFS


# the class where the information which is gossiped between nodes is hold
# first version: save classes (in X "rdf:type" Y triples, Y)
class Gossiped:
    #parse method to json?
    
    def __init__(self):
        self.types = []
        self.subclass = []
        self.subproperty = []
    
    def serializeToJson(self):
        return json.dumps([t for t in self.types]) # otherwise set cannot be converted to json
    
    def parseJson(self, json_str):
        for t in json.loads(json_str):
            self.types.append(URIRef(t)) # cause the URI is passed as a string  
    
    @staticmethod
    def extractFromJson(json_str):
        ret = Gossiped()
        ret.parseJson(json_str)
        return ret
    
    @staticmethod
    def extractFromGraph(graph): # sort of factory
        ret = Gossiped()
        ret.types = ret.extractRdfTypes(graph)
        return ret
    
    @staticmethod
    def extractRdfTypes(graph): # sort of factory     
        ret = set()
        for t in graph.triples((None, RDF.type, None)): # return a Gossiped piece of info from own Graph
            if not isinstance(t[2], BNode): # to avoid blank nodes
                ret.add(t[2])
        return ret
    
    def isCandidate(self, template, ontology):
        """ Tests if according to this gossiped piece of information
            the node which have it is candidate to answer a query or not """
        if template[1]!=None:
            if template[1]==RDF.type and template[2]!=None:
                return self.__hasClassesFromThisType(ontology, template[2])
            else: return self.__doesPredicateBelongToClass(ontology, template[1])
        elif template[2]!=None:
            return template[2] in self.types
        else: return True # we cannot predict anything with a subject or an object
            
    def __hasClassesFromThisType(self, ontology, rdftype):
        if rdftype in self.types:
            return True
        return False
        # already done if it was expanded
        #for subtype, _, _ in ontology.triples((None, RDFS.subClassOf, rdftype)):
        #    if subtype in self.types:
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
        for t in self.types:
            dom = dom or self.__hasClassesOfDomain(ontology, predicate, t)
            #ran = dom or self.__hasClassesOfRange(ontology, predicate, t)
            # with "AND" could be quite restrictive, we may have classes which whose type we don't know (because we don't infer anything)
            if dom: return True
        return False
    
    def isEmpty(self):
        return not self.types and not self.subclass and not self.subproperty
        
        #if template[0]!=None:
        #    isSubjectInstanceOfClass(template[0])
        # is predicate of rdf:type?
        # object?