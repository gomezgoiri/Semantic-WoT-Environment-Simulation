'''
Created on Feb 18, 2012

@author: tulvur
'''
import StringIO
import unittest
from rdflib import Graph
from rdflib import URIRef
from strateval.triplespace.gossiping.gossiping_mechanism import GossipingBase

tbox_data = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix weather:  <http://knoesis.wright.edu/ssw/ont/weather.owl#> .

weather:Class2 rdfs:subClassOf weather:Class1 .
"""

class GossipedTest(unittest.TestCase):

    def test_addGossip(self):
        tbox = Graph().parse(StringIO.StringIO(tbox_data),format="n3")
        gb = GossipingBase(tbox)
        
        gb.addGossip('nodeA', '["http://knoesis.wright.edu/ssw/ont/weather.owl#Class2"]', expand=False)
        self.assertEquals(1, len(gb.gossips['nodeA'].types))
        self.assertTrue( URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#Class2') in gb.gossips['nodeA'].types )
        
        gb.addGossip('nodeB', '["http://knoesis.wright.edu/ssw/ont/weather.owl#Class2"]', expand=True)
        self.assertTrue( URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#Class2') in gb.gossips['nodeB'].types )
        self.assertTrue( URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#Class1') in gb.gossips['nodeB'].types )

if __name__ == '__main__':
    unittest.main()