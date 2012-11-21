'''
Created on Sep 10, 2012

@author: tulvur
'''
import unittest
from rdflib import RDF, URIRef, Graph, Namespace
from clueseval.clues.predicate_based import PredicateBasedClue
from commons.utils import SemanticFilesLoader

class TestStats(unittest.TestCase):
    
    def setUp(self):
        self.clue = PredicateBasedClue()
        self.clue.schemas = [('deusto', URIRef('http://deusto.es/')), ('meneame',URIRef('http://meneame.net#'))]
        self.clue.predicates = [URIRef('http://deusto.es/mola'),URIRef('http://meneame.net#chachi'),URIRef('http://deusto.es/guay')]
    
    def test_parseJson_toJson(self):
        clue2 = PredicateBasedClue()
        clue2.parseJson(self.clue.toJson())
        
        for name, uri in self.clue.schemas:
            self.assertTrue((name,uri) in clue2.schemas)
            
        for p in self.clue.predicates:
            self.assertTrue(p in clue2.predicates)
            
    def test_eq(self):
        self.assertNotEquals(self.clue, 12)
        
        clue2 = PredicateBasedClue()
        clue2.schemas = [('deusto', URIRef('http://deusto.es/')), ('meneame',URIRef('http://meneame.net#'))]
        clue2.predicates = [URIRef('http://deusto.es/mola'),URIRef('http://meneame.net#chachi'),URIRef('http://deusto.es/guay')]
        self.assertEquals(self.clue, clue2)
    
    def _load_clues(self, semanticPath):
        sfl = SemanticFilesLoader(semanticPath)
        names = sfl.selectStations()
        graphs = {}
        sfl.loadGraphsJustOnce(names, graphs)
        
        clues = {}
        for node_name in graphs:
            if node_name not in ('ontology','ontology_expanded'):
                clues[node_name] = PredicateBasedClue()
                
                union = Graph()
                for g in graphs[node_name]:
                    for t in g.triples((None, None, None)):
                        union.add(t)
                        # arreglar lo de los namespaces en la union!
                   
                clues[node_name].parseGraph(union)
                
        return clues
    
    def _assert_candidates(self, expected_candidates, template, clues):
        for name, clue in clues.iteritems():
            if name in expected_candidates:
                self.assertTrue( clue.isCandidate(template), msg="%s expected to be a candidate for template %s"%(name, template) )
            else:
                self.assertFalse( clue.isCandidate(template), msg="%s not expected to be a candidate for template %s"%(name, template) )
    
    def test_isCandidate(self):
        clues = self._load_clues('../sample_files')
        
        SSN = Namespace('http://purl.oclc.org/NET/ssnx/ssn#')
        SSN_WEATHER = Namespace('http://knoesis.wright.edu/ssw/ont/weather.owl#')
        WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
        BIZKAI_STATION = Namespace('http://helheim.deusto.es/bizkaisense/resource/station/')
        DC = Namespace('http://purl.org/dc/elements/1.1/')
        
        # TEST
        templates = (
          # based on type
          (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
          (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
          (None, SSN.observedProperty, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
                                              # knoesis defines its own observedProperty in SSN_OBSERV
          (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
          (None, DC.identifier, None),
        )
                
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6','bizkaisense/ALGORT','bizkaisense/ABANTO','aemet/08001','aemet/08002','luebeck/211','luebeck/300','morelab/aitor-almeida','morelab/aitor-gomez-goiri'), templates[0], clues ) # too general predicate, flood all
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6'), templates[1], clues )
        self._assert_candidates( ('bizkaisense/ALGORT','bizkaisense/ABANTO','aemet/08001','aemet/08002','luebeck/211','luebeck/300'), templates[2], clues ) # knoesis tienen una observerProperty de otra ontologia distinta
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6','bizkaisense/ALGORT','bizkaisense/ABANTO','aemet/08001','aemet/08002', 'luebeck/211','luebeck/300','morelab/aitor-almeida','morelab/aitor-gomez-goiri'), templates[3], clues ) # No clue, flood all
        self._assert_candidates( ('bizkaisense/ALGORT','bizkaisense/ABANTO'), templates[4], clues )
        # self._assert_candidates( ('4UT01','7CAMPA','A01','A02','A03','ABANTO','ABMN6','ACOC1','ACON5'), templates[0], clues )

if __name__ == '__main__':
    unittest.main()
    