'''
Created on Sep 10, 2012

@author: tulvur
'''
import unittest
from clueseval.clues.storage.memory import AbstractStore

class TestAbstractStore(unittest.TestCase):
    """
    @prefix _10: <http://purl.oclc.org/NET/muo/ucum/unit/plane-angle/>.
@prefix _11: <http://helheim.deusto.es/bizkaisense/resource/station/>.
@prefix _12: <http://sweet.jpl.nasa.gov/2.3/propFraction.owl#>.
@prefix _13: <http://purl.org/dc/elements/1.1/>.
@prefix _14: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/Humedad/01012011/00#>.
@prefix _15: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/Temp/01102010/00#>.
@prefix _16: <http://purl.oclc.org/NET/muo/ucum/unit/temperature/>.
@prefix _17: <http://sweet.jpl.nasa.gov/2.3/propTemperature.owl#>.
@prefix _18: <http://sweet.jpl.nasa.gov/2.3/matrCompound.owl#>.
@prefix _19: <http://sweet.jpl.nasa.gov/2.3/matrElementalMolecule.owl#>.
@prefix _20: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/O3/01012011/00#>.
@prefix _21: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/VelV/01102010/00#>.
@prefix _22: <http://sweet.jpl.nasa.gov/2.3/propSpeed.owl#>.
@prefix _23: <http://purl.oclc.org/NET/muo/ucum/unit/fraction/>.
@prefix _24: <http://purl.oclc.org/NET/ssnx/meteo/WM30#>.
@prefix _3: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/SO2/01012010/00#>.
@prefix _4: <http://purl.oclc.org/NET/ssnx/ssn#>.
@prefix _5: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/NO2/01012011/00#>.
@prefix _6: <http://www.loa-cnr.it/ontologies/DUL.owl#>.
@prefix _7: <http://helheim.deusto.es/bizkaisense/ucum-extended.owl#>.
@prefix _8: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/NO/01012011/00#>.
@prefix _9: <http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/DirV/01012011/00#>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
    """
    
    def setUp(self):
        self.store = FakeStore()
        
    def tearDown(self):
        pass
    
    def test_get_n_most_representative_chars(self):        
        c = self.store._get_n_most_representative_chars("propFractionCool", 1)
        self.assertEquals("p", c)
        
        c = self.store._get_n_most_representative_chars("propFractionCool", 2)
        self.assertEquals("pF", c)
        
        c = self.store._get_n_most_representative_chars("propFractionCool", 3)
        self.assertEquals("pFC", c)
        
        c = self.store._get_n_most_representative_chars("propFractionCool", 6)
        self.assertEquals("pFCool", c)
        
        c = self.store._get_n_most_representative_chars("propFractionCool", 10)
        self.assertEquals("pFCoolxxxx", c)
        
        c = self.store._get_n_most_representative_chars("lower-case", 3)
        self.assertEquals("low", c)
        
        c = self.store._get_n_most_representative_chars("023lower-case", 5)
        self.assertEquals("lower", c)
    
    def test_generate_prefix_name_from_dot_owl_uri(self):
        prefix_name = self.store.generate_prefix_name(u"http://sweet.jpl.nasa.gov/2.3/propFraction.owl#")
        self.assertEquals("pFr", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEquals("rdf", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://purl.oclc.org/NET/muo/ucum/unit/plane-angle/")
        self.assertEquals("pla", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://purl.org/dc/elements/1.1/")
        self.assertEquals("ele", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/Humedad/01012011/00#")
        self.assertEquals("Hum", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://helheim.deusto.es/bizkaisense/resource/station/ABANTO/SO2/01012010/00#")
        self.assertEquals("SOx", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://sweet.jpl.nasa.gov/2.3/matrElementalMolecule.owl#")
        self.assertEquals("mEM", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://helheim.deusto.es/bizkaisense/ucum-extended.owl#")
        self.assertEquals("ucu", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://purl.oclc.org/NET/ssnx/ssn#")
        self.assertEquals("ssn", prefix_name)
        
        prefix_name = self.store.generate_prefix_name(u"http://purl.oclc.org/NET/ssnx/meteo/WM30#")
        self.assertEquals("WMx", prefix_name)
        
        
    
class FakeStore(AbstractStore):
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def add_clue(self, node_name, clue_json):
        pass
    
    def toJson(self):
        pass
    
    def fromJson(self, json_str):
        pass
    
    def get_query_candidates(self, template):
        pass


if __name__ == '__main__':
    unittest.main()
    