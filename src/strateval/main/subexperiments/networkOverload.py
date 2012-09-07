'''
Created on Jan 30, 2012

@author: tulvur
'''
import random
from rdflib import URIRef
from rdflib import RDF
from strateval.main.parametrize import getStationNames
from strateval.database.execution import ExecutionSet
from strateval.database.execution import Execution
from strateval.database.parametrization import Parametrization
from strateval.main.showResults import RequestsResults
from strateval.main.showResults import PlotStats
from strateval.main.showResults import AveragedAttributeGetter

# Assess network overload

EXPERIMENT_ID = 'network_overload'


def parametrize(semanticPath):
    possibleNodes = getStationNames(semanticPath)
    es = ExecutionSet(experiment_id=EXPERIMENT_ID)
    
    # important: this for before the strategy for, to have the same nodes in both simulations
    for numNodes in (2, 5, 10, 50, 100, 150):
        nodes = random.sample(possibleNodes, numNodes)
        
        for strategy in (Parametrization.negative_broadcasting, Parametrization.centralized, Parametrization.gossiping):
            params = Parametrization(strategy=strategy,
                                     amountOfQueries=100,
                                     writeFrequency = 1000,
                                     nodes=nodes,
                                     simulateUntil = 60000,
                                     queries = ((None, RDF.type, URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#RainfallObservation')),
                                                (URIRef('http://dev.morelab.deusto.es/bizkaisense/resource/station/ABANTO'), None, None)
                                                ,)
                                )
            params.save()
            
            # repeating each experiment's execution, we increase the accuracy of the obtained data
            for i in range(1):
                execution = Execution(parameters=params)
                execution.save()
                es.addExecution(execution)
    
    es.save()
    
    
def getNeededRequests(execution_set):
    def expectedRequests(params):
        total = 0
        for q in params.queries:
            for node in params.nodes:
                savedresults = RequestsResults.objects(station_name=node)
                savedresults = filter(lambda r: r.query==q, savedresults)
                if savedresults:
                    if savedresults[0].has_result:
                        total += params.amountOfQueries
                else:
                    raise Exception("Result not expected, you should run calculateExpectedResults.py again.")        
        return total
    
    params = []
    for ex in execution_set.executions:
        par_id = ex.parameters.id
        if par_id not in params:
            params.append(par_id)
    
    x = []
    y_xindex = {}
    for p_id in params:
        params = Parametrization.objects(id=p_id).first()
        num_nodes = len(params.nodes)
        if num_nodes not in x: # both strategies may have the same configurations, so they should have the same "expectations"
            x.append(num_nodes)
            y_xindex[num_nodes] = expectedRequests(params)
    
    x.sort()
    y = []
    for x_val in x:
        y.append(y_xindex[x_val])
        
    return x, y, None
            
def show(): # number of necessary requests / total requests 
    for executionSet in ExecutionSet.get_simulated().filter(experiment_id=EXPERIMENT_ID):
        ps = PlotStats(xAxisName="Number of nodes",
                       yAxisName="Number of requests") #, titleText="Communication efficiency"
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.total, executionSet)
        ps.plotLines(ag, (Parametrization.centralized, Parametrization.negative_broadcasting, Parametrization.gossiping))
        
        ps.plotLine(getNeededRequests(executionSet), "Best possible case", 'k:')
        
        ps.show()
        
        # KB/s sent
        ps = PlotStats(xAxisName="Number of nodes",
                       yAxisName="Data exchanged (KB/s)")
        ag = AveragedAttributeGetter(lambda ex: ex.results.data_exchanged/(60*1024), executionSet)
        ps.plotLines(ag, (Parametrization.centralized, Parametrization.negative_broadcasting, Parametrization.gossiping))
        ps.show()
        break

if __name__ == '__main__':    
    #parametrize('../../../../files/semantic')
    show()