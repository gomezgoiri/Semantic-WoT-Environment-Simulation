'''
Created on Feb 7, 2012

@author: tulvur
'''
import StringIO
import unittest
from rdflib import Graph
from rdflib import URIRef
from rdflib import RDF
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.DLP.DLNormalization import NormalFormReduction

from netuse.triplespace.gossiping.gossiped import Gossiped
from netuse.main.simulate import loadGraphsJustOnce


semanticPath = '../../../files/semantic'


response = """
@prefix om-owl:  <http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#> .
@prefix sens-obs:  <http://knoesis.wright.edu/ssw/> .
@prefix wgs84:   <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix weather:  <http://knoesis.wright.edu/ssw/ont/weather.owl#> .

sens-obs:LocatedNearRelAFTY
      a       om-owl:LocatedNearRel ;
      om-owl:distance "0.3832"^^xsd:float ;
      om-owl:hasLocation <http://sws.geonames.org/5826623/> ;
      om-owl:uom weather:miles .

sens-obs:System_AFTY
      a       om-owl:System ;
      om-owl:ID "AFTY" ;
      om-owl:hasLocatedNearRel
              sens-obs:LocatedNearRelAFTY ;
      om-owl:hasSourceURI <http://mesowest.utah.edu/cgi-bin/droman/meso_base.cgi?stn=AFTY> ;
      om-owl:parameter weather:_WindDirection , weather:_RelativeHumidity , weather:_AirTemperature , weather:_DewPoint , weather:_WindSpeed , weather:_WindGust ;
      om-owl:processLocation
              sens-obs:point_AFTY .

sens-obs:point_AFTY
      a       wgs84:Point ;
      wgs84:alt "6211"^^xsd:float ;
      wgs84:lat "42.73333"^^xsd:float ;
      wgs84:long "-110.93583"^^xsd:float .
      
sens-obs:Observation_WindSpeed_AFTY_2003_4_4_2_15_00
      a       weather:WindSpeedObservation ;
      om-owl:observedProperty
              weather:_WindSpeed ;
      om-owl:procedure sens-obs:System_AFTY ;
      om-owl:result sens-obs:MeasureData_WindSpeed_AFTY_2003_4_4_2_15_00 ;
      om-owl:samplingTime sens-obs:Instant_2003_4_4_2_15_00 .   
"""

class GossipedTest(unittest.TestCase):

    def test_extractRdfTypes(self):
        graph = Graph().parse(StringIO.StringIO(response),format="n3")
        types = Gossiped().extractRdfTypes(graph)
        
        for expected in (URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#System'),
              URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#WindSpeedObservation'),
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#LocatedNearRel'),
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#Point') ):
            self.assertTrue( expected in types )
    
    def expand_ontology(self, tBoxGraph):
        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
        NormalFormReduction(tBoxGraph)
        network.setupDescriptionLogicProgramming(tBoxGraph)
        network.feedFactsToAdd(generateTokenSet(tBoxGraph))
        return network.inferredFacts
    
    def test_isCandidate(self):
        loaded_graphs = {}
        loadGraphsJustOnce((), semanticPath, loaded_graphs)
        base_ontologies = loaded_graphs['ontology']
        base_ontologies += self.expand_ontology(base_ontologies)
        
        graph = Graph().parse(StringIO.StringIO(response), format="n3")
        gossip = Gossiped.extractFromGraph(graph)
        
        
        self.checkCandidatenessByObject(gossip, base_ontologies,
            (URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#System'),
              URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#WindSpeedObservation'),
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#LocatedNearRel'),
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#Point'),
               ) )
        
        self.checkCandidatenessByRDFTypeObject(gossip, base_ontologies,
            (URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#System'),
              URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#WindSpeedObservation'),
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#LocatedNearRel'),
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#Point'),
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#Location'), # Point is a subClassOf Location and SpatialThings
              
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing')) )
        
        self.checkCandidatenessByPredicate(gossip, base_ontologies,
            (URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#hasLocation'),
              URIRef('http://www.w3.org/2003/01/geo/wgs84_pos#alt'), # alt belongs to SpatialThing, Point is subclass of SpatialThing and does not have range
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#parameter'), # System is subclass of Process which is the one which has parameter
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#observedProperty'), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
              URIRef('http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#hasLocatedNearRel'),
              ) )
        
    def checkCandidatenessByRDFTypeObject(self, gossip, ontology, uris):
        for uri in uris:
            self.assertTrue( gossip.isCandidate((None, RDF.type, uri), ontology), "No class of type %s"%(uri) )
            
    def checkCandidatenessByObject(self, gossip, ontology, uris):
        for uri in uris:
            self.assertTrue( gossip.isCandidate((None, None, uri), ontology) )
                        
    def checkCandidatenessByPredicate(self, gossip, ontology, uris):
        for uri in uris:
            self.assertTrue( gossip.isCandidate((None, uri, None), ontology), "No class with this predicate: %s"%(uri) )


if __name__ == '__main__':
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Start simulation process.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    
    # before you pas control to unittest code, so that the latter code doesn't try to interpret your command line options again when you've already dealt with them
    del sys.argv[1:]
    unittest.main()