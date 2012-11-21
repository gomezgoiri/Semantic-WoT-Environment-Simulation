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
                
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6'), templates[0], clues ) # TODO if one of the predicates a well-known one, take into account other elements of the template (such as object in this case)
        # Parece que los de knoesis no usan SSN como tal, solo su sensor-obvervation.owl (que sera alguna version previa)
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6','aemet/08001','aemet/08002','luebeck/300'), templates[1], clues )
        # El caso de Luebeck es aun mas curioso, no todas las plataformas tienen definido el geo.
        self._assert_candidates( ('bizkaisense/ALGORT','bizkaisense/ABANTO','aemet/08001','aemet/08002','luebeck/211','luebeck/300'), templates[2], clues )
        self._assert_candidates( ('bizkaisense/ALGORT','bizkaisense/ABANTO'), templates[3], clues )
        # Almeida does not offer a description of him resource
        self._assert_candidates( ('bizkaisense/ALGORT','bizkaisense/ABANTO','morelab/aitor-gomez-goiri'), templates[4], clues )
        # self._assert_candidates( ('4UT01','7CAMPA','A01','A02','A03','ABANTO','ABMN6','ACOC1','ACON5'), templates[0], clues )

if __name__ == '__main__':
    unittest.main()