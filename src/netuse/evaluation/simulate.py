'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
from rdflib import Graph

# "SimulationTrace" instead of "Simulation" to debug
from SimPy.Simulation import initialize, simulate

from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.DLP.DLNormalization import NormalFormReduction

from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.execution import ExecutionSet
from netuse.results import G

from multiprocessing import Process



def performSimulation(execution, semanticPath, preloadedGraph={}):
    loadGraphsJustOnce(execution.parameters.nodes, semanticPath, preloadedGraph)
    
    initialize()
    G.setNewExecution(execution)
    
    nodes = NodeGenerator(execution.parameters)
    nodes.generateNodes()
    
    activity = ActivityGenerator(execution.parameters, preloadedGraph)
    activity.generateActivity()
    
    # activate
    cool_down = 500
    simulate(until=execution.parameters.simulateUntil+cool_down)
    
    G.shutdown()


def expand_ontology(tBoxGraph):
    rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
    NormalFormReduction(tBoxGraph)
    network.setupDescriptionLogicProgramming(tBoxGraph)
    network.feedFactsToAdd(generateTokenSet(tBoxGraph))
    return network.inferredFacts

def loadGraphsJustOnce(nodeNames, semanticPath, loadedGraph):
    datasetPath = semanticPath+"/dataset"
    ontologiesPath = semanticPath+"/base_ontologies"
    
    if 'ontology' not in loadedGraph:
        loadedGraph['ontology'] = Graph()
        dirList=os.listdir(ontologiesPath)
        for fname in dirList:
            if not os.path.isdir(ontologiesPath+'/'+fname):
                loadedGraph['ontology'] += Graph().parse(ontologiesPath+"/"+fname)
        #loadedGraph['ontology_expanded'] = expand_ontology(loadedGraph['ontology'])
    
    for node_name in nodeNames:
        if node_name not in loadedGraph:
            loadedGraph[node_name] = []
            dirList=os.listdir(datasetPath)
            for fname in dirList:
                if not os.path.isdir(datasetPath+'/'+fname):
                    if fname.find(node_name)!=-1:
                        loadedGraph[node_name].append( Graph().parse(datasetPath+"/"+fname, format="n3") )

def simulateUnsimulatedExecutionSet(semanticPath):
    loadedGraphs = {}
    
    for es in ExecutionSet.get_unsimulated():
        #es.delete()
        processes = []
        for ex in es.executions:
            if ex.parameters!=None:
                from multiprocessing import Process
                p = Process(target=performSimulation, args=(ex, semanticPath, loadedGraphs))
                p.start()
                
                #performSimulation(ex, semanticPath, loadedGraphs)
                print "New simulation: %s"%(ex.parameters)
                processes.append(p)
        for p in processes:
            p.join()
        break # just one simulation (ExecutionSet) per execution
        

if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/workspaces/doctorado/files/semantic'
    
    parser = argparse.ArgumentParser(description='Start simulation process.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    simulateUnsimulatedExecutionSet(semanticPath)