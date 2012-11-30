from rdflib import URIRef, Namespace, RDF

from testing.utils import TimeRecorder
from testing.memory_usage import memory

from netuse.results import G
from netuse.evaluation.simulate import BasicModel
from netuse.tracers import FileTracer
from netuse.nodes import NodeGenerator
from netuse.activity import ActivityGenerator
from commons.utils import SemanticFilesLoader
from netuse.database.parametrization import Parametrization
from netuse.evaluation.utils import ParametrizationUtils, Parameters

# This script generates a simulation and records its trace in a file.
# Used to check the functionalities under really simple simulation conditions.


class TraceAndLoadFilesModel(BasicModel):
        
    def initialize(self):
        G.setNewExecution(None, tracer=FileTracer('/tmp/trace.txt'))
        super(TraceAndLoadFilesModel, self).initialize()
    
    def runModel(self):
        preloadedGraph = {}
        sfl = SemanticFilesLoader(G.dataset_path)
        sfl.loadGraphsJustOnce(self.parameters.nodes, preloadedGraph)
        
        # To log SimPy's events:
        #trace.tchange(outfile=open(r"/tmp/simulation.log","w"))
        
        self.initialize()
        
        nodes = NodeGenerator(self.parameters, simulation=self)
        nodes.generateNodes()
        self.stoppables.extend( nodes.getNodes() )
        
        activity = ActivityGenerator(self.parameters, preloadedGraph, simulation=self)
        activity.generateActivity()
        
        recorder = TimeRecorder()
        recorder.start()
        
        self.simulate( until=self.parameters.simulateUntil )
        print "Memory consumption: %0.2f GB"%(memory()/(1024*1024*1024))
        
        recorder.stop()
        print recorder


def main():
    from netuse.sim_utils import OwnArgumentParser
    parser = OwnArgumentParser('Memory integration test')
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
    templates = ((None, SSN.observationResult, None),)
    
    
    p = ParametrizationUtils('memory_integration_test', '/home/tulvur/dev/dataset', None)
    params = Parameters (
            simulateUntil = 400000,
            strategy = Parametrization.our_solution,
            amountOfQueries = 1000,
            writeFrequency = 10000,
            queries = templates,
            nodes = p.get_random_nodes(100),
            numConsumers = 100
         )
    
    model = TraceAndLoadFilesModel( p.create_parametrization(params) )
    model.runModel()


if __name__ == '__main__':
    main()