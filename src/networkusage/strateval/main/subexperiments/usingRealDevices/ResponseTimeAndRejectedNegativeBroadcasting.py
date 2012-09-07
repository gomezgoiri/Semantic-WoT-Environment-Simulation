'''
Created on Jan 30, 2012

@author: tulvur
'''
import random
from rdflib import URIRef
from rdflib import RDF
from threading import Thread
from matplotlib.pyplot import show

from strateval.devices import XBee
from strateval.devices import FoxG20, RegularComputer
from strateval.main.parametrize import getStationNames
from strateval.database.execution import ExecutionSet
from strateval.database.execution import Execution
from strateval.database.parametrization import Parametrization
from strateval.main.showResults import PlotStats
from strateval.main.showResults import AveragedAttributeGetter


EXPERIMENT_ID = 'overloading_real_devices_with_negative_broadcasting'


# En una red de 100 XBees, con cuantas requests/minuto se satura?
# Y en una de FoxG20s?
def parametrize(semanticPath):
    possibleNodes = getStationNames(semanticPath)
    es = ExecutionSet(experiment_id=EXPERIMENT_ID)
    
    # important: this for before the strategy for, to have the same nodes in both simulations
    numNodes = 100
    for numQueries in (100, 500, 1000, 1500, 2000):
        for devType in (FoxG20.TYPE_ID, XBee.TYPE_ID,):
            for strategy in (Parametrization.negative_broadcasting):
                nodes = random.sample(possibleNodes, numNodes)
                nodeTypes = []
                nodeTypes += (devType,)*numNodes
                
                params = Parametrization(strategy=strategy,
                                         amountOfQueries=numQueries,
                                         writeFrequency=0, # it does not affect with NB
                                         nodes=nodes,
                                         nodeTypes=nodeTypes,
                                         simulateUntil = 60000,
                                         queries = ((None, RDF.type, URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#RainfallObservation')),)
                                    )
                params.save()
                # repeating each experiment's execution, we increase the accuracy of the obtained data
                for i in range(2):
                    execution = Execution(parameters=params)
                    execution.save()
                    es.addExecution(execution)
    
    es.save()

def show():
    for executionSet in ExecutionSet.get_simulated().filter(experiment_id=EXPERIMENT_ID):
    #for executionSet in ExecutionSet.objects(Q(execution_date__ne=None) & Q(experiment_id=EXPERIMENT_ID)):
        x_axis_getter = lambda params: params.amountOfQueries
        relevancyFilter = lambda params, lineName: params.nodeTypes[0]==lineName
        
        ps = PlotStats(xAxisName="Number of queries",
                       yAxisName="Average response time (ms)") #, titleText="Response time using real devices")
        ag = AveragedAttributeGetter(lambda ex: ex.results.response_time_mean, executionSet,
                                     x_axis_getter=x_axis_getter,
                                     relevancyFilter=relevancyFilter)
        ps.plotLines(ag, (FoxG20.TYPE_ID, XBee.TYPE_ID))
        ps.show()
        
        ps2 = PlotStats(xAxisName="Number of queries",
                       yAxisName="Number of requests rejected",
                       titleText=None)
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.server_error, executionSet,
                                     x_axis_getter=x_axis_getter,
                                     relevancyFilter=relevancyFilter)
        ps2.plotLines(ag, (FoxG20.TYPE_ID, XBee.TYPE_ID))
        ps2.show()
        
        break

if __name__ == '__main__':
    #parametrize('../../../../../files/semantic')
    show()