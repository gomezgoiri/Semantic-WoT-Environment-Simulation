'''
Created on Feb 17, 2012

@author: tulvur
'''
import numpy
from rdflib import RDF, URIRef, Graph
from clueseval.evaluation.utils import loadGraphsJustOnce, selectStations
from clueseval.evaluation.precision.diagram import DiagramGenerator
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue


SSN = 'http://purl.oclc.org/NET/ssnx/ssn#'
SSN_OBSERV = 'http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#'
SSN_WEATHER = 'http://knoesis.wright.edu/ssw/ont/weather.owl#'
WGS84 = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
CF = 'http://purl.oclc.org/NET/ssnx/cf/cf-property#'
CF_FEATURE = 'http://purl.oclc.org/NET/ssnx/cf/cf-feature#'
SMART_KNIFE = 'http://purl.oclc.org/NET/ssnx/product/smart-knife#'
BIZKAI_STATION = 'http://dev.morelab.deusto.es/bizkaisense/resource/station/'


def getQueriableNodes(gossipings, template):
    ret = []
    for node_name, gossip in gossipings.items():
        if gossip.isCandidate(template):
            ret.append( node_name )
    return ret

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

def createGossips(graphs):
    gossips = {}
    gossips['schema'] = {}
    gossips['predicate'] = {}
    gossips['class'] = {}
    
    total = len(graphs)
    count = 0
    
    for node_name in graphs:
        if node_name not in ('ontology','ontology_expanded'):
            print "\rCreating gossips... (%%%.2f)"%(count*100.0/total)
            
            gossips['schema'][node_name] = SchemaBasedClue()
            gossips['predicate'][node_name] = PredicateBasedClue()
            gossips['class'][node_name] = ClassBasedClue(graphs['ontology'])
            
            union = Graph()
            for g in graphs[node_name]:
                for t in g.triples((None, None, None)):
                    union.add(t)
                    # arreglar lo de los namespaces en la union!
               
            for g_type in gossips.keys():
                gossips[g_type][node_name].parseGraph(g)
                if g_type=='class':
                    gossips[g_type][node_name].expand()
            #print "gossip added for", node_name
            count += 1
    return gossips

def calculatePAndRForAllQueries(graphs, gossips):
    results = {}
    results["precision"] = {}
    results["recall"] = {}
    
    for t in templates:
        relevant_nodes = nodesWithoutEmptyResponse(graphs, t)
        #print relevant_nodes
        
        for g_type in gossips.keys():
            if g_type not in results["precision"]:
                results["precision"][g_type] = []
                results["recall"][g_type] = []
            
            queriable_nodes = getQueriableNodes(gossips[g_type], t)
            pandr = calculatePrecisionAndRecall(queriable_nodes, relevant_nodes)
            
            results["precision"][g_type].append(pandr[0])
            results["recall"][g_type].append(pandr[1])
            
            #print queriable_nodes
            #print "%s (precision & recall):"%(g_type), pandr
            
    return results
            
if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/workspaces/doctorado/files/semantic'
    
    parser = argparse.ArgumentParser(description='Evaluate gossiping strategies.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    args = parser.parse_args()
    
    
    names = selectStations(semanticPath)
    graphs = {}
    loadGraphsJustOnce(names, semanticPath, graphs)
    
    gossips = createGossips(graphs)
    
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
    
    results = calculatePAndRForAllQueries(graphs, gossips)
    print results
    
    g = DiagramGenerator('Recall', 'Recall for each query', results["recall"])
    g.save('recall.png')
    
    g = DiagramGenerator('Precision', 'Precision for each query', results["precision"])
    g.save('precision.png')
    
    #g.show()