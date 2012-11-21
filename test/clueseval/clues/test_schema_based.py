'''
Created on Sep 10, 2012

@author: tulvur
'''
import unittest
from StringIO import StringIO
from rdflib import URIRef, ConjunctiveGraph, RDF, Namespace
from rdflib.Graph import Graph
from clueseval.clues.schema_based import SchemaBasedClue
from commons.utils import SemanticFilesLoader

class SchemaBasedClueTestCase(unittest.TestCase):
    
    def setUp(self):
        self.clue = SchemaBasedClue()
        self.clue.schemas = [URIRef('http://deusto.es/'), URIRef('http://deusto.es/guay'), URIRef('http://deusto.es/chachi')]
    
    def test_parseJson_toJson(self):
        clue2 = SchemaBasedClue()
        
        clue2.parseJson(self.clue.toJson())
        
        for u in self.clue.schemas:
            self.assertTrue(u in clue2.schemas)
    
    # Method from parent_clue
    def test_filterBizkaisenseSchemas(self):
        schemas = ( ('_1', URIRef('http://helheim.deusto.es/emaldi/rules/')),
                    ('_8', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/')),
                    ('_17', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/CO/01052009/00#')),
                    ('_20', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/DirV/01052009/00#')),
                    ('_15', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/Humedad/01052009/00#')),
                    ('_12', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/NO/01052009/00#')),
                    ('_21', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/NO2/01012008/00#')),
                    ('_9', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/O3/01012008/00#')),
                    ('_10', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/PM10/01012008/00#')),
                    ('_31', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/PM25/01052009/00#')),
                    ('_23', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/Presion/01012008/00#')),
                    ('_18', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/SO2/01012008/00#')),
                    ('_16', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/Temp/01102010/00#')),
                    ('_14', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/UVRad/01012010/00#')),
                    ('_26', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/VelV/01102010/00#'))
                  )
        
        schemas2 = self.clue.filterBizkaisenseSchemas( list(schemas) )
        
        self.assertEquals( 3, len(schemas2) )
        self.assertTrue( schemas[0] in schemas2 )
        self.assertTrue( schemas[1] in schemas2 )
        self.assertTrue( ('ALGORT', URIRef('http://helheim.deusto.es/bizkaisense/resource/station/ALGORT/')) in schemas2 )
    
    # Method from parent_clue
    def test_extractNamespaces_from_normal_graph(self):
        graph = Graph().parse(StringIO("<http://www.deusto.es/fakesubject> <http://www.deusto.es/fakepredicate> <http://www.deusto.es/fakeobject> .\n"), format="nt")
        #graph.bind("deusto", "http://www.deusto.es/", override=True)
        #print list(graph.namespaces())
        
        clue2 = SchemaBasedClue()
        schemas = clue2._extractNamespaces(graph)
        
        self.assertTrue(URIRef('http://www.deusto.es/') in [s[1] for s in schemas])
    
    # Method from parent_clue
    def test_extractNamespaces_from_conjuctive_graph(self):
        graphs = ConjunctiveGraph(store='default')
        
        gr1 = Graph().parse(StringIO("<http://URIRef('http://deusto.es/')deusto.es/fakesubject> <http://www.deusto.es/fakepredicate> <http://www.deusto.es/fakeobject> .\n"), format="nt")
        #gr1.bind("deusto", "http://www.deusto.es/", override=True)
        
        graph = Graph(graphs.store, URIRef('http://www.deusto.es/mygraph'))
        graph += gr1
        
        clue2 = SchemaBasedClue()
        schemas = clue2._extractNamespaces(graphs)
        
        self.assertTrue(URIRef('http://www.deusto.es/') in [s[1] for s in schemas])
    
    def test_eq(self):
        self.assertNotEquals(self.clue, 12)
        
        clue2 = SchemaBasedClue()
        clue2.schemas = [URIRef('http://deusto.es/'), URIRef('http://deusto.es/guay'), URIRef('http://deusto.es/chachi')]
        self.assertEquals(self.clue, clue2)

    
    def _load_clues(self, semanticPath):
        sfl = SemanticFilesLoader(semanticPath)
        names = sfl.selectStations()
        graphs = {}
        sfl.loadGraphsJustOnce(names, graphs)
        
        clues = {}
        for node_name in graphs:
            if node_name not in ('ontology','ontology_expanded'):
                clues[node_name] = SchemaBasedClue()
                
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
                
        self._assert_candidates( ('knoesis/4UT01','knoesis/A01','knoesis/A02','knoesis/A03','knoesis/ABMN6','knoesis/ACOC1','knoesis/ACON5'), templates[0], clues )
        self._assert_candidates( ('knoesis/4UT01','knoesis/A01','knoesis/A02','knoesis/A03','knoesis/ABMN6','knoesis/ACOC1','knoesis/ACON5'), templates[1], clues )
        self._assert_candidates( ('bizkaisense/7CAMPA','bizkaisense/ABANTO'), templates[2], clues ) # parece que los de knoesis no usan SSN como tal, solo su sensor-obvervation.owl (que sera alguna version previa)
        self._assert_candidates( ('bizkaisense/ABANTO'), templates[3], clues )
        self._assert_candidates( ('bizkaisense/7CAMPA','bizkaisense/ABANTO'), templates[4], clues )
        # self._assert_candidates( ('4UT01','7CAMPA','A01','A02','A03','ABANTO','ABMN6','ACOC1','ACON5'), templates[0], clues )

if __name__ == '__main__':
    unittest.main()