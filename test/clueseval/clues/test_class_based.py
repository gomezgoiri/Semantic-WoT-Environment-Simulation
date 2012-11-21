'''
Created on Sep 10, 2012

@author: tulvur
'''
import unittest
from rdflib import RDF, Graph, Namespace
from clueseval.clues.class_based import ClassBasedClue
from commons.utils import SemanticFilesLoader

class TestStats(unittest.TestCase):
    
    def _load_clues(self, semanticPath):
        sfl = SemanticFilesLoader(semanticPath)
        names = sfl.selectStations()
        graphs = {}
        sfl.loadGraphsJustOnce(names, graphs)
        
        clues = {}
        for node_name in graphs:
            if node_name not in ('ontology','ontology_expanded'):
                clues[node_name] = ClassBasedClue(graphs['ontology'])
                
                union = Graph()
                for g in graphs[node_name]:
                    for t in g.triples((None, None, None)):
                        union.add(t)
                        # arreglar lo de los namespaces en la union!
                   
                clues[node_name].parseGraph(union)
                clues[node_name].expand() # TODO mock expansion!
                
        return clues
    
    def _assert_candidates(self, expected_candidates, template, clues):
        for name, clue in clues.iteritems():
            if name in expected_candidates:
                self.assertTrue( clue.isCandidate(template), msg="%s expected to be a candidate for template %s"%(name, template) )
            else:
                self.assertFalse( clue.isCandidate(template), msg="%s not expected to be a candidate for template %s"%(name, template) )
    
    def test_isCandidate(self):
        clues = self._load_clues('../../../files')
        
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
                
        self._assert_candidates( ('knoesis/ABMN6','knoesis/ACON5'), templates[0], clues )
        self._assert_candidates( ('knoesis/4UT01','knoesis/A01','knoesis/A02','knoesis/A03','knoesis/ABMN6','knoesis/ACOC1','knoesis/ACON5'), templates[1], clues )
        self._assert_candidates( (), templates[2], clues ) # SSN subproperty de DUL
        self._assert_candidates( ('knoesis/4UT01','bizkaisense/7CAMPA','knoesis/A01','knoesis/A02','knoesis/A03','bizkaisense/ABANTO','knoesis/ABMN6','knoesis/ACOC1','knoesis/ACON5'), templates[3], clues )
        self._assert_candidates( (), templates[4], clues )
        # self._assert_candidates( ('4UT01','7CAMPA','A01','A02','A03','ABANTO','ABMN6','ACOC1','ACON5'), templates[0], clues )

if __name__ == '__main__':
    unittest.main()
    