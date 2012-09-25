'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
import datetime
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



def performSimulation(execution, preloadedGraph={}):
    print "New simulation: %s"%(execution.parameters)
    
    loadGraphsJustOnce(execution.parameters.nodes, G.dataset_path, preloadedGraph)
    
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
    datasetPath = semanticPath+"/data"
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


def mark_execution(execution):
    ''' This method is used to warn another processes that this one is already processing it.'''
    execution.execution_date = datetime.datetime.now
    execution.save()

def execute_all_concurrently(executions):
    processes = []
    for ex in executions:
        if ex.execution_date!=None and ex.parameters!=None:
            mark_execution(ex)
            p = Process(target=performSimulation, args=(ex,))
            p.start()
            processes.append(p)
    for p in processes:
        p.join()
    
def execute_once_each_time(executions):
    # loadedGraphs = {}
    for ex in executions:
        if ex.execution_date!=None and ex.parameters!=None:
            mark_execution(ex)            
            # In a new process to ensure that the memory is freed after that
            p = Process(target=performSimulation, args=(ex,))
            p.start()
            p.join()
            # Otherwise, to avoid loading graphs each time...
            #performSimulation(ex, loadedGraphs)

def simulateUnsimulatedExecutionSet():
    one_es_per_execution = True # just one simulation (ExecutionSet) per execution
    
    for es in ExecutionSet.get_unsimulated:
        #execute_all_concurrently(es.executions)
        execute_once_each_time(es.executions)
        
        if one_es_per_execution:
            break

# Entry point for setup.py
def main():
    from netuse.sim_utils import OwnArgumentParser
    parser = OwnArgumentParser('Start simulation process.')
    parser.parse_args()
    simulateUnsimulatedExecutionSet()
    
if __name__ == '__main__':
    main()