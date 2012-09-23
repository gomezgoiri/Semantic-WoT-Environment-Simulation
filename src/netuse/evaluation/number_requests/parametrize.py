'''
Created on Jan 30, 2012

@author: tulvur
'''
from rdflib import URIRef, RDF, Namespace
from netuse.evaluation.utils import ParametrizationUtils
from netuse.database.parametrization import Parametrization
from netuse.database.results import RequestsResults


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
    
    
    SSN = Namespace('http://purl.oclc.org/NET/ssnx/ssn#')
    SSN_OBSERV = Namespace('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#')
    SSN_WEATHER = Namespace('http://knoesis.wright.edu/ssw/ont/weather.owl#')
    WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
    CF = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-property#')
    CF_FEATURE = Namespace('http://purl.oclc.org/NET/ssnx/cf/cf-feature#')
    SMART_KNIFE = Namespace('http://purl.oclc.org/NET/ssnx/product/smart-knife#')
    BIZKAI_STATION = Namespace('http://dev.morelab.deusto.es/bizkaisense/resource/station/')
    
    
    templates = (
      # based on type
      (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
      (None, RDF.type, SSN_OBSERV.Observation), # in many nodes, but, without inference?
      # predicate based
      (None, SSN_OBSERV.hasLocation, None), # domain LocatedNearRel
      (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
      (None, SSN_OBSERV.observedProperty, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
      (None, SMART_KNIFE.hasMeasurementPropertyValue, None), # domain ssn:MeasurementProperty child of ssn:Property
      (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
    )
    
    # important: this for before the strategy for, to have the same nodes in both simulations
    for numNodes in (2, 5, 10, 50, 100, 150):
        p.createDefaultParametrization(Parametrization.negative_broadcasting,
                               amountOfQueries = 100,
                               writeFrequency = 10000,
                               simulateUntil = 60000,
                               queries = templates,
                               numNodes = numNodes,
                               numConsumers = 1 # no importa
                               )
        
        for numConsumers in (1, 10, 100):
            if numConsumers<=numNodes:
                    p.createDefaultParametrization(Parametrization.our_solution,
                                                   amountOfQueries = 100,
                                                   writeFrequency = 10000,
                                                   simulateUntil = 60000,
                                                   queries = templates,
                                                   numNodes = numNodes,
                                                   numConsumers = numConsumers
                                                   )