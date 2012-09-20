'''
Created on Feb 17, 2012

@author: tulvur
'''
import numpy
from rdflib import Graph
from clueseval.evaluation.utils import selectStations, loadGraphsJustOnce
from clueseval.evaluation.length.diagram import DiagramGenerator
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue



def createGossips(graphs):
    gossips = {}
    gossips['schema'] = {}
    gossips['predicate'] = {}
    gossips['class'] = {}
    
    for node_name in graphs:
        if node_name not in ('ontology','ontology_expanded'):
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
    return gossips

def calculateLenghtAvgAndDev(gossips):
    results = {}
    results['schema'] = {}
    results['predicate'] = {}
    results['class'] = {}
           
    for g_type in gossips.keys():
        lengths = []
        for gs in gossips[g_type].values():
            lengths.append( len(gs.toJson()) )
            
        results[g_type]['avg'] = numpy.average(lengths)
        results[g_type]['std'] = numpy.std(lengths)
            
    return results
            
if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/workspaces/doctorado/files/semantic/'
    
    parser = argparse.ArgumentParser(description='Evaluate gossiping strategies.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    args = parser.parse_args()
    
    
    names = selectStations(semanticPath)
    graphs = {}
    loadGraphsJustOnce(names, semanticPath, graphs)
    
    gossips = createGossips(graphs)
    
    results = calculateLenghtAvgAndDev(gossips)
    print results
    
    g = DiagramGenerator("Length of the clues shared", '', results)
    g.save('length.pdf')
    
    #g.show()