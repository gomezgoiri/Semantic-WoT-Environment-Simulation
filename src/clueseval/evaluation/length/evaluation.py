'''
Created on Feb 17, 2012

@author: tulvur
'''
import json
from rdflib import Graph
from commons.utils import SemanticFilesLoader
from clueseval.evaluation.length.diagram import DiagramGenerator
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue


def createClues(graphs):
    gossips = {}
    gossips['prefix'] = {}
    gossips['predicate'] = {}
    gossips['class'] = {}
    
    for node_name in graphs:
        if node_name not in ('ontology','ontology_expanded'):
            gossips['prefix'][node_name] = SchemaBasedClue()
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

def calculateLenghts(clues):
    results = {}
    results['prefix'] = {}
    results['predicate'] = {}
    results['class'] = {}
           
    for c_type in clues.keys():
        lengths = []
        for node_name, clue in clues[c_type].iteritems():
            if len(clue.toJson())>500:
                print node_name
                print clue.toJson()
            lengths.append( len(clue.toJson()) )
        results[c_type] = lengths
    
    return results
            
if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/dataset/'
    
    parser = argparse.ArgumentParser(description='Evaluate gossiping strategies.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    args = parser.parse_args()
    
    
    sfl = SemanticFilesLoader(semanticPath)
    names = sfl.selectStations(semanticPath)
    graphs = {}
    sfl.loadGraphsJustOnce(names, graphs)
    
    clues = createClues(graphs)
    
    results = calculateLenghts(clues)
    
    f = open('/tmp/clues_length.json', 'w')
    f.write(json.dumps(results))
    f.close()