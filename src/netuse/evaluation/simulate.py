'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
import random
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF

# "SimulationTrace" instead of "Simulation" to debug
from SimPy.Simulation import initialize, simulate

from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.DLP.DLNormalization import NormalFormReduction

from netuse.main.parametrize import getStationNames
from netuse.devices import XBee
from netuse.devices import FoxG20, RegularComputer
from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.execution import ExecutionSet
from netuse.database.results import Results, RequestsResults
from netuse.results import G
from netuse.statistic import Stats
from netuse.database.parametrization import Parametrization



def performSimulation(parameters, semanticPath, preloadedGraph={}):
    loadGraphsJustOnce(parameters.nodes, semanticPath, preloadedGraph)
    
    initialize()
    G.newExecution()
    
    nodes = NodeGenerator(parameters)
    nodes.generateNodes()
    
    activity = ActivityGenerator(parameters, preloadedGraph)
    activity.generateActivity()
    
    stats = Stats(parameters, nodes)
    stats.onSimulationEnd(simulationEnd=parameters.simulateUntil)
    
    # activate
    cool_down = 500
    simulate(until=parameters.simulateUntil+cool_down)
    
    return stats.getExecutionInfo()

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

def storeExecutionResult(execution, executionInfo):
    rr = RequestsResults(found=executionInfo["requests"]["found"],
                         not_found=executionInfo["requests"]["not-found"],
                         server_error=executionInfo["requests"]["server-error"],
                         timeout=executionInfo["requests"]["timeout"],
                         success=executionInfo["requests"]["success"],
                         failure=executionInfo["requests"][ "failure"],
                         total=executionInfo["requests"]["total"])
    rr.save()
    r = Results(requests=rr,
                response_time_mean=executionInfo["time_needed"],
                data_exchanged=executionInfo["data-exchanged"])
    r.save()
    
    execution.results = r
    execution.save()

def simulateUnsimulatedExecutionSet(semanticPath):
    loadedGraphs = {} 
    for es in ExecutionSet.get_unsimulated():
        #es.delete()
        for ex in es.executions:
            if ex.parameters!=None:
                storeExecutionResult( ex, performSimulation(ex.parameters, semanticPath, loadedGraphs) )
                print "New simulation: %s"%(ex.parameters)
        break # just one simulation (ExecutionSet) per execution

def adhocSimulation(semanticPath):
    possibleNodes = getStationNames(semanticPath)
    numNodes = 150
    nodes = random.sample(possibleNodes, numNodes)
    
    nodeTypes = []
    nodeTypes += (FoxG20.TYPE_ID,)*numNodes
    #nodeTypes += (XBee.TYPE_ID,)*100
    params = Parametrization(strategy=Parametrization.gossiping,
                             amountOfQueries = 100,
                             writeFrequency = 1000,
                             nodes = nodes,
                             nodeTypes=nodeTypes,
                             simulateUntil = 60000,
                             queries = ((None, RDF.type, URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#RainfallObservation')),
                                                (URIRef('http://dev.morelab.deusto.es/bizkaisense/resource/station/ABANTO'), None, None)
                                                ,)
                             )
    s = performSimulation(params, semanticPath)
    print s



if __name__ == '__main__':
    import argparse
    
    semanticPath = '../../../files/semantic'
    
    parser = argparse.ArgumentParser(description='Start simulation process.')
    parser.add_argument('-ah','--ad-hoc', default='False', dest='adhoc',
                help='Ad-hoc simulation without saving anything.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    if args.adhoc=='True':
        adhocSimulation(semanticPath);
    else:
        semanticPath = args.dataset_path
        simulateUnsimulatedExecutionSet(semanticPath)