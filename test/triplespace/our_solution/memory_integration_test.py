from SimPy.Simulation import initialize, simulate

from rdflib import URIRef, Namespace, RDF

from netuse.results import G, FileTracer
from netuse.nodes import NodeGenerator
from netuse.evaluation.simulate import loadGraphsJustOnce
from netuse.activity import ActivityGenerator
from netuse.evaluation.utils import ParametrizationUtils
from netuse.database.parametrization import Parametrization

# This script generates a simulation and records its trace in a file.
# Used to check the functionalities under really simple simulation conditions.

def performSimulation(parameters):    
    preloadedGraph = {}
    loadGraphsJustOnce(parameters.nodes, '/home/tulvur/dev/workspaces/doctorado/files/semantic', preloadedGraph)
    
    initialize()
    G.setNewExecution(None, tracer=FileTracer('/tmp/trace.txt'))
    
    nodes = NodeGenerator(parameters)
    nodes.generateNodes()
    
    activity = ActivityGenerator(parameters, preloadedGraph)
    activity.generateActivity()
    
    # activate
    cool_down = 500
    simulate(until=parameters.simulateUntil+cool_down)
    
    G.shutdown()


def main():
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
#      (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
#      (None, RDF.type, SSN_OBSERV.Observation), # in many nodes, but, without inference?
      # predicate based
#      (None, SSN_OBSERV.hasLocation, None), # domain LocatedNearRel
#      (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
      (None, SSN_OBSERV.hasLocatedNearRel, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
#      (None, SMART_KNIFE.hasMeasurementPropertyValue, None), # domain ssn:MeasurementProperty child of ssn:Property
#      (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
    )
    
    temp = ((None, URIRef('http://www.deusto.es/fakepredicate'), None),)
    
    param = p.getDefaultParametrization(Parametrization.our_solution,
                                                   amountOfQueries = 100,
                                                   writeFrequency = 10000,
                                                   simulateUntil = 60000,
                                                   queries = templates,
                                                   numNodes = 50,
                                                   numConsumers = 50
                                                   )
    print param
    performSimulation(param) 



if __name__ == '__main__':
    main()