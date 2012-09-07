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


EXPERIMENT_ID = 'response_time'


def parametrize(semanticPath):
    possibleNodes = getStationNames(semanticPath)
    es = ExecutionSet(experiment_id=EXPERIMENT_ID)
    
    # important: this for before the strategy for, to have the same nodes in both simulations
    for numQueries in (100, 500, 1000): #1 0, 50,, 100, 200, 500, 1000):
        for strategy in (Parametrization.negative_broadcasting, Parametrization.centralized, Parametrization.gossiping):
            nodes = random.sample(possibleNodes, 100)
            nodeTypes = []
            nodeTypes += (FoxG20.TYPE_ID,)*50
            nodeTypes += (XBee.TYPE_ID,)*50
            
            params = Parametrization(strategy=strategy,
                                     amountOfQueries=numQueries,
                                     writeFrequency = 0,
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


class ShowPlot(Thread):
    def __init__(self, plot):
        Thread.__init__(self)
        self.plot = plot
    
    def run(self):
        self.plot.show()

def show():
    for executionSet in ExecutionSet.get_simulated().filter(experiment_id=EXPERIMENT_ID):
        x_axis_getter = lambda params: params.amountOfQueries
        
        ps = PlotStats(xAxisName="Number of queries",
                       yAxisName="Average response time (ms)",
                       titleText="Response time using real devices")
        ag = AveragedAttributeGetter(lambda ex: ex.results.response_time_mean, executionSet, x_axis_getter=x_axis_getter)
        ps.plotLines(ag, (Parametrization.negative_broadcasting, Parametrization.centralized, Parametrization.gossiping))
        ps.show()
        
        ps2 = PlotStats(xAxisName="Number of queries",
                       yAxisName="Number of requests rejected",
                       titleText=None)
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.server_error, executionSet, x_axis_getter=x_axis_getter)
        ps2.plotLines(ag, (Parametrization.negative_broadcasting, Parametrization.centralized, Parametrization.gossiping))
        ps2.show()
        
        break

if __name__ == '__main__':    
    #parametrize('../../../../files/semantic')
    show()