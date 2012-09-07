'''
Created on Feb 17, 2012

@author: tulvur
'''
import random
import numpy
import copy
import json
from rdflib import RDF, URIRef, Graph

from strateval.database.gossipings import Gossipings
from strateval.main.parametrize import getStationNames
from strateval.main.simulate import loadGraphsJustOnce
from strateval.triplespace.gossiping.gossiping_mechanism import GossipingBase
from strateval.triplespace.gossiping.gossiping_mechanism import Gossiped

SSN = 'http://purl.oclc.org/NET/ssnx/ssn#'
SSN_OBSERV = 'http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#'
SSN_WEATHER = 'http://knoesis.wright.edu/ssw/ont/weather.owl#'
WGS84 = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
CF = 'http://purl.oclc.org/NET/ssnx/cf/cf-property#'
CF_FEATURE = 'http://purl.oclc.org/NET/ssnx/cf/cf-feature#'
SMART_KNIFE = 'http://purl.oclc.org/NET/ssnx/product/smart-knife#'
BIZKAI_STATION = 'http://dev.morelab.deusto.es/bizkaisense/resource/station/'

def nodesWithoutEmptyResponse(graphs, template):
    def hasTriple(graph, template):
        for t in graph.triples(template):
            return True
        return False
    
    ret = []
    for name in graphs:
        if name not in ('ontology','ontology_expanded'):
            for g in graphs[name]:
                if hasTriple(g, template):
                    ret.append( name )
                    break
    return ret

# precision is the fraction of retrieved instances that are relevant
# recall is the fraction of relevant instances that are retrieved
def calculatePrecisionAndRecall(retrieved_nodes, relevant_nodes):
    if len(retrieved_nodes)==0 and len(relevant_nodes)==0:
        return 1, 1
      
    intersec = float(len( numpy.intersect1d(retrieved_nodes, relevant_nodes) ))
        
    precision = 0 if len(retrieved_nodes)==0 else intersec / len(retrieved_nodes)
    recall =  0 if len(relevant_nodes)==0 else  intersec / len(relevant_nodes)
    
    return precision, recall

def showStatistics():
    nodes_unrepeated = set()
    total_classes = set()
    total_classes_expanded = set()
    normal =[]
    expanded = []
    
    for node in Gossipings.objects():
        if node in nodes_unrepeated:
            print node, "repeated"
        else:
            nodes_unrepeated.add(node)
        for t in node.gossips:
            total_classes.add(t)
        for t in node.gossips_expanded:
            total_classes_expanded.add(t)
        
        normal.append( len(node.gossips) )
        expanded.append( len(node.gossips_expanded) )
    
    print "Number of nodes:", len(nodes_unrepeated)
    print "Number of total classes:", len(total_classes)
    print "    (expanded :%i)"%(len(total_classes_expanded))
    print "Number of classes stored in each node: %i (std dev: %i)"%(numpy.average(normal), numpy.std(normal))
    print "Number of classes expanded in each node: %i (std dev: %i)"%(numpy.average(expanded), numpy.std(expanded))


if __name__ == '__main__':
    semanticPath = '../../../../../files/semantic'
    graphs = {}
    
    possibleNodes = getStationNames(semanticPath)
    notInDatabaseNodes = copy.copy(possibleNodes)
    
    #numNodes = 10
    #names = random.sample(possibleNodes, numNodes)
    names = possibleNodes
    loadGraphsJustOnce(names, semanticPath, graphs)
    
    #showStatistics()
    
    for g in Gossipings.objects:
        notInDatabaseNodes.remove( g.node )
    
    normal_gossiping = GossipingBase(graphs['ontology'])
    expanded_gossiping = GossipingBase(graphs['ontology'])
    for node_name in graphs:
        if node_name not in ('ontology','ontology_expanded'):
            if node_name in notInDatabaseNodes:
                cg = Graph() # conjuctive graph
                for g in graphs[node_name]:
                    cg += g
                normal_gossiping.addGossip( node_name, Gossiped.extractFromGraph(cg), expand=False )
                expanded_gossiping.addGossip( node_name, Gossiped.extractFromGraph(cg), expand=True )
                
                g = Gossipings(node=node_name,
                          gossips = [str(t) for t in normal_gossiping.gossips[node_name].types],
                          gossips_expanded =  [str(t) for t in expanded_gossiping.gossips[node_name].types] )
                g.save()
            else:
                gossip = Gossiped()
                gossip.types = [URIRef(u) for u in Gossipings.objects(node=node_name).first().gossips]
                normal_gossiping.addGossip(node_name, gossip, expand=False)
                
                gossip = Gossiped()
                gossip.types = [URIRef(u) for u in Gossipings.objects(node=node_name).first().gossips_expanded]
                expanded_gossiping.addGossip(node_name, gossip, expand=False)
            print "gossip added for", node_name
    
    # TEST
    templates = (
      # based on type
      (None, RDF.type, URIRef(SSN_WEATHER+'RainfallObservation')), # in 43 nodes
      (None, RDF.type, URIRef(SSN_OBSERV+'Observation')), # in many nodes, but, without inference?
      # predicate based
      (None, URIRef(SSN_OBSERV+'hasLocation'), None), # domain LocatedNearRel
      (None, URIRef(WGS84+'long'), None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
      (None, URIRef(SSN_OBSERV+'observedProperty'), None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
      (None, URIRef(SMART_KNIFE+'hasMeasurementPropertyValue'), None), # domain ssn:MeasurementProperty child of ssn:Property
      (URIRef(BIZKAI_STATION+'ABANTO'), None, None), # given an instance, we cannot predict anything
    )
    
    results = []
    for t in templates:
        relevant_nodes = nodesWithoutEmptyResponse(graphs, t)
        retrieved_nodes_without_inference = normal_gossiping.getQueriableNodes(t)
        retrieved_nodes_with_inference = expanded_gossiping.getQueriableNodes(t)
        pandrWithout = calculatePrecisionAndRecall(retrieved_nodes_without_inference, relevant_nodes)
        pandrWith = calculatePrecisionAndRecall(retrieved_nodes_with_inference, relevant_nodes)
        
        print t
        print relevant_nodes
        print "Without:", pandrWithout
        print "With:", pandrWith
        results.append((pandrWithout[0],pandrWithout[1],pandrWith[0],pandrWith[1]))
    
    i = 1
    print "\n\n\n"
    for r in results:
        print 't%i & %s & %s & %s & %s \\\\'%(i,round(r[0], 3),round(r[1], 3),round(r[2], 3),round(r[3], 3))
        i += 1
        