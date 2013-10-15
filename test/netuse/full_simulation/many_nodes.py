# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

from rdflib import URIRef, Namespace, RDF

from testing.utils import TimeRecorder
from testing.memory_usage import memory

from netuse.results import G
from netuse.nodes import NodeManager
from commons.utils import SemanticFilesLoader
from netuse.activity import ActivityGenerator
from netuse.tracers.http import FileHTTPTracer
from netuse.tracers.udp import FileUDPTracer
from netuse.network_models import NetworkModelManager
from netuse.evaluation.simulate import BasicModel
from netuse.evaluation.utils import ParametrizationUtils, Parameters
from netuse.triplespace.network.discovery.discovery import DiscoveryFactory
from netuse.database.parametrization import Parametrization, ParametrizableNetworkModel, NetworkModel

# This script generates a simulation and records its trace in a file.
# Used to check the functionalities under really simple simulation conditions.


class TraceAndLoadFilesModel(BasicModel):
        
    def initialize(self):
        G.setNewExecution( None,
                           tracer = FileHTTPTracer('/tmp/trace.txt'),
                           udp_tracer = FileUDPTracer('/tmp/trace_udp.txt') )
        super(TraceAndLoadFilesModel, self).initialize()
    
    def runModel(self):
        preloadedGraph = {}
        sfl = SemanticFilesLoader(G.dataset_path)
        sfl.loadGraphsJustOnce(self.parameters.nodes, preloadedGraph)
        
        # To log SimPy's events:
        #trace.tchange(outfile=open(r"/tmp/simulation.log","w"))
        
        self.initialize()
                
        ActivityGenerator.create(self.parameters, preloadedGraph, simulation=self)
        self.stoppables.extend( NodeManager.getNodes() )
        
        recorder = TimeRecorder()
        recorder.start()
        
        self.simulate( until=self.parameters.simulateUntil )
        print "Memory consumption: %0.2f GB"%(memory()/(1024*1024*1024))
        
        recorder.stop()
        print recorder


def main():
    from commons.utils import OwnArgumentParser
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
            discovery = DiscoveryFactory.SIMPLE_DISCOVERY, #SIMPLE_DISCOVERY MDNS_DISCOVERY
            strategy = Parametrization.our_solution,
            amountOfQueries = 1000,
            writeFrequency = 10000,
            queries = templates,
            nodes = p.get_random_nodes(100),
            numConsumers = 100,
            network_model = ParametrizableNetworkModel( type = NetworkModelManager.chaotic_netmodel ) # NetworkModel()
         )
    
    model = TraceAndLoadFilesModel( p.create_parametrization(params) )
    model.runModel()


if __name__ == '__main__':
    main()