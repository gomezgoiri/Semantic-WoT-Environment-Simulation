'''
Created on Feb 17, 2012

@author: tulvur
'''
import json
import numpy
from rdflib import RDF, Graph, Namespace
from commons.utils import SemanticFilesLoader
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue


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
                gossips[g_type][node_name].parseGraph(union)
                if g_type=='class':
                    gossips[g_type][node_name].expand()
            #print "gossip added for", node_name
            count += 1
    return gossips

def calculatePAndRForAllQueries(graphs, clues, templates):
    results = {}
    results["precision"] = {}
    results["recall"] = {}
    
    for t in templates:
        relevant_nodes = nodesWithoutEmptyResponse(graphs, t)
        #print t, relevant_nodes
        
        for g_type in clues.keys():
            if g_type not in results["precision"]:
                results["precision"][g_type] = []
                results["recall"][g_type] = []
            
            queriable_nodes = getQueriableNodes(clues[g_type], t)
            pandr = calculatePrecisionAndRecall(queriable_nodes, relevant_nodes)
            
            results["precision"][g_type].append(pandr[0])
            results["recall"][g_type].append(pandr[1])
            
            #print queriable_nodes
            #print "%s (precision & recall):"%(g_type), pandr
            
    return results

    
def main():
    import argparse
    
    semanticPath = '/home/tulvur/dev/workspaces/doctorado/files/semantic'
    
    parser = argparse.ArgumentParser(description='Evaluate gossiping strategies.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    args = parser.parse_args()
    
    
    sfl = SemanticFilesLoader(semanticPath)
    names = sfl.selectStations()
    graphs = {}
    sfl.loadGraphsJustOnce(names, graphs)
    
    gossips = createGossips(graphs)
    
    SSN = Namespace('http://purl.oclc.org/NET/ssnx/ssn#')
    SSN_OBSERV = Namespace('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#')
    SSN_WEATHER = Namespace('http://knoesis.wright.edu/ssw/ont/weather.owl#')
    WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
    CF = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-property#')
    CF_FEATURE = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-feature#')
    SMART_KNIFE = Namespace('http://purl.oclc.org/NET/ssnx/product/smart-knife#')
    BIZKAI_STATION = Namespace('http://helheim.deusto.es/bizkaisense/resource/station/')
    DC = Namespace('http://purl.org/dc/elements/1.1/')
    
    # TEST
    templates = (
      # based on type
      (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
      (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
      (None, SSN.observedProperty, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
                                          # knoesis defines its own observedProperty in SSN_OBSERV
      (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
      (None, DC.identifier, None),
    )
    
    
    results = calculatePAndRForAllQueries(graphs, gossips, templates)
    f = open('/tmp/clues_precision_recall.json', 'w')
    f.write(json.dumps(results))
    f.close()


if __name__ == '__main__':   
    main()