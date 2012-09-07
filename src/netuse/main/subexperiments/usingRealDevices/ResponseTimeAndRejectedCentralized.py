'''
Created on Jan 30, 2012

@author: tulvur
'''
import random
from rdflib import URIRef
from threading import Thread
from matplotlib.pyplot import show

from netuse.devices import XBee
from netuse.devices import FoxG20, RegularComputer
from netuse.main.parametrize import getStationNames
from netuse.database.execution import ExecutionSet
from netuse.database.execution import Execution
from netuse.database.parametrization import Parametrization
from netuse.main.showResults import PlotStats
from netuse.main.showResults import AveragedAttributeGetter


EXPERIMENT_ID = 'overloading_foxg20_with_centralized'


# Usando un FoxG20 a modo de servidor, con a que frecuencia de escritura por segundo se saturaria?
def parametrize(semanticPath):
    possibleNodes = getStationNames(semanticPath)
    es = ExecutionSet(experiment_id=EXPERIMENT_ID)
    
    devType = FoxG20.TYPE_ID
    for numNodes in (50, 100, 500, 1000):
        for writeFreq in (1000, 5000, 10000, 20000, 30000):
            
            if numNodes<=len(possibleNodes):
                nodes = random.sample(possibleNodes, numNodes)
            else:
                nodes = []
                nodes += possibleNodes
                nodes += [ 'node' + str(i) for i in range(100,numNodes) ]
            
            nodeTypes = (devType,)*numNodes
            
            params = Parametrization(strategy=Parametrization.centralized,
                                     amountOfQueries=0, # may not be the worst problem with centralized
                                     writeFrequency=writeFreq,
                                     nodes=nodes,
                                     nodeTypes=nodeTypes,
                                     simulateUntil = 60000,
                                     queries = ((None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_SnowDepth")),))
            params.save()
            # repeating each experiment's execution, we increase the accuracy of the obtained data
            for i in range(1):
                execution = Execution(parameters=params)
                execution.save()
                es.addExecution(execution)
    
    es.save()

def show():
    for executionSet in ExecutionSet.get_simulated().filter(experiment_id=EXPERIMENT_ID):
    #for executionSet in ExecutionSet.objects(Q(execution_date__ne=None) & Q(experiment_id=EXPERIMENT_ID)):
        x_axis_getter = lambda params: params.writeFrequency
        relevancyFilter = lambda params, numNodes: len(params.nodes)==int(numNodes)
        
        ps = PlotStats(xAxisName="Write frequency",
                       yAxisName="Average response time (ms)",
                       titleText="Response time for centralized strategy using FoxG20")
        ag = AveragedAttributeGetter(lambda ex: ex.results.response_time_mean, executionSet,
                                     x_axis_getter=x_axis_getter,
                                     relevancyFilter=relevancyFilter)
        ps.plotLines(ag, ('50', '100', '500', '1000'))
        ps.show()
        
        ps2 = PlotStats(xAxisName="Write frequency",
                       yAxisName="Number of requests rejected",
                       titleText=None)
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.server_error, executionSet,
                                     x_axis_getter=x_axis_getter,
                                     relevancyFilter=relevancyFilter)
        ps2.plotLines(ag, ('50', '100', '500', '1000'))
        ps2.show()
        
        break

if __name__ == '__main__':
    #parametrize('../../../../../files/semantic')
    show()