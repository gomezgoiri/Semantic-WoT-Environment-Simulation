'''
Created on Jan 30, 2012

@author: tulvur
'''
from rdflib import URIRef, RDF
from netuse.evaluation.utils import ParametrizationUtils
from netuse.database.parametrization import Parametrization
from netuse.main.showResults import RequestsResults


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


if __name__ == '__main__':
    p = ParametrizationUtils('network_usage', '/home/tulvur/dev/workspaces/doctorado/files/semantic')
    
    # important: this for before the strategy for, to have the same nodes in both simulations
    for numNodes in (2, 5, 10, 50, 100, 150):
        for numConsumers in (1, 10, 100):
            for strategy in (Parametrization.negative_broadcasting, Parametrization.gossiping):
                p.createDefaultParametrization(strategy,
                                               amountOfQueries = 100,
                                               writeFrequency = 1000,
                                               simulateUntil = 60000,
                                               queries = ((None, RDF.type, URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#RainfallObservation')),
                                                          (URIRef('http://dev.morelab.deusto.es/bizkaisense/resource/station/ABANTO'), None, None)
                                                          ,),
                                               numNodes = numNodes,
                                               numConsumers = numConsumers
                                               )