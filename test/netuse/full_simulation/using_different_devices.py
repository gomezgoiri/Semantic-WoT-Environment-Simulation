from rdflib import URIRef, Namespace, RDF

from netuse.results import G
from netuse.tracers import FileTracer
from netuse.nodes import NodeGenerator
from netuse.activity import ActivityGenerator
from netuse.evaluation.simulate import BasicModel
from netuse.evaluation.utils import ParametrizationUtils, Parameters
from netuse.database.parametrization import Parametrization
from netuse.devices import XBee, SamsungGalaxyTab, FoxG20, Server

# This script generates a simulation and records its trace in a file.
# Used to check the functionalities under really simple simulation conditions.

class SimpleTraceModel(BasicModel):
        
    def initialize(self):
        G.setNewExecution(None, tracer=FileTracer('/tmp/trace.txt'))
        super(SimpleTraceModel, self).initialize()
    
    def runModel(self):        
        self.initialize()
        
        nodes = NodeGenerator(self.parameters, simulation=self)
        nodes.generateNodes()
        self.stoppables.extend( nodes.getNodes() )
        
        ActivityGenerator.create(self.parameters, None, simulation=self)
        
        self.simulate( until=self.parameters.simulateUntil )


def main():
    from commons.utils import OwnArgumentParser
    parser = OwnArgumentParser('WP selection integration test')
    parser.parse_args() # do nothing with the args (already done)
    
    
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
    
    numNodes = 300
    # 1 server, 10% of galaxys, 25% of FoxG20
    nodeTypes = (Server.TYPE_ID,)*1 + (SamsungGalaxyTab.TYPE_ID,)*((int)(numNodes*0.1)) + (FoxG20.TYPE_ID,)*((int)(numNodes*0.25))
    # Remaining devices, are XBees
    nodeTypes += (XBee.TYPE_ID,)*(numNodes-len(nodeTypes))
    

    p = ParametrizationUtils('integration_test', G.dataset_path, None)
    params = Parameters (
                simulateUntil = 60000,
                strategy = Parametrization.our_solution,
                amountOfQueries = 100,
                writeFrequency = 10000,
                queries = temp,
                nodes = p.get_random_nodes(numNodes),
                numConsumers = 100,
                nodeTypes = nodeTypes
             )
    
    model = SimpleTraceModel( p.create_parametrization(params) )
    model.runModel()


if __name__ == '__main__':
    main()