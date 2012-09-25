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
    print "New simulation: %s"%(execution.parameters)
    
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

def execute_all_concurrently(executions):
    processes = []
    for ex in executions:
        if ex.execution_date!=None and ex.parameters!=None:
            from multiprocessing import Process
            p = Process(target=performSimulation, args=(ex, semanticPath))
            p.start()
            processes.append(p)
    for p in processes:
        p.join()
    
def execute_once_each_time(executions):
    # loadedGraphs = {}
    for ex in executions:
        if ex.execution_date!=None and ex.parameters!=None:
            # In a new process to ensure that the memory is freed after that
            from multiprocessing import Process
            p = Process(target=performSimulation, args=(ex, semanticPath))
            p.start()
            p.join()
            # Otherwise, to avoid loading graphs each time...
            #performSimulation(ex, semanticPath, loadedGraphs)

def simulateUnsimulatedExecutionSet(semanticPath):
    one_es_per_execution = True # just one simulation (ExecutionSet) per execution
    
    for es in ExecutionSet.get_unsimulated():
        #execute_all_concurrently(es.executions)
        execute_once_each_time(es.executions)
        
        if one_es_per_execution:
            break


if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/workspaces/doctorado/files/semantic'
    
    parser = argparse.ArgumentParser(description='Start simulation process.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    simulateUnsimulatedExecutionSet(semanticPath)