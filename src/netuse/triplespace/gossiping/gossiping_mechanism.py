'''
Created on Feb 6, 2012

@author: tulvur
'''
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF

from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.DLP.DLNormalization import NormalFormReduction
from FuXi.Horn.HornRules import HornFromN3

from netuse.triplespace.gossiping.gossiped import Gossiped

# module where the gossiped info is stored
class GossipingBase:
    
    def __init__(self, ontologyGraph):
        self.ontology = ontologyGraph
        self.gossips = {} # key: name of node, value: gossip
    
    def expand_gossip(self, gossip):
        abox = Graph()
        i = 0
        for t in gossip.types:
            abox.add( (URIRef("http://el%i"%(i)), RDF.type, t) )
            i += 1
        
        _, _, network = SetupRuleStore(makeNetwork=True)
        NormalFormReduction(self.ontology)
        for rule in HornFromN3('http://www.agfa.com/w3c/euler/rdfs-rules.n3'): #'../lib/python-dlp/fuxi/test/pD-rules.n3'): #HornFromDL(self.tBoxGraph):
            network.buildNetworkFromClause(rule)
        network.feedFactsToAdd(generateTokenSet(self.ontology))
        network.feedFactsToAdd(generateTokenSet(abox))
        
        new_gossip = Gossiped.extractFromGraph(network.inferredFacts)
        for t in gossip.types:
            new_gossip.types.add(t)
        return new_gossip
    
    def addGossip(self, nodeName, gossip, expand=False):
        g = gossip if isinstance(gossip, Gossiped) else Gossiped.extractFromJson(gossip)
            
        if nodeName not in self.gossips.keys():
            if expand: g = self.expand_gossip(g)
            self.gossips[nodeName] = g
        else:
            print "Already gossiped!"
            
    
    # return the nodes which may have relevant data for a given query
    def getQueriableNodes(self, template):
        ret = []
        for nodeName, gossip in self.gossips.iteritems():
            if gossip.isCandidate(template, self.ontology):
                ret.append(nodeName)
        return ret
    
    # listOfAllNodes is a list of Node objects
    def getUngossiped(self, listOfAllNodes):
        ret = []
        for n in listOfAllNodes:
            if n.name not in self.gossips.keys():
                ret.append(n)
        return ret