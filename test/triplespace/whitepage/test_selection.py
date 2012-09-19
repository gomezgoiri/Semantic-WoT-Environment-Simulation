import unittest
import urllib
from rdflib import URIRef
from rdflib.Literal import Literal, _XSD_NS
from netuse.triplespace.network.discovery import DiscoveryRecord
from netuse.triplespace.our_solution.whitepage.selection import WhitepageSelector


class FakeNode():
    
    def __init__(self, memory='1MB', storage='1MB',
                 joined_since=1, battery_lifetime=DiscoveryRecord.INFINITE_BATTERY, sac=False, is_whitepage=False):
        self.discovery_record = DiscoveryRecord(memory, storage, joined_since, sac, battery_lifetime)
    
    def tuple_to_str(self, tuple):
        return str(tuple[0]) + tuple[1]
    
    def __repr__(self):
        return "(" + self.tuple_to_str(self.discovery_record.memory) + ", " + self.tuple_to_str(self.discovery_record.storage) + ", " + self.discovery_record.battery_lifetime + ")"


class WhitepageSelectorTestCase(unittest.TestCase):
    
    def setUp(self):
        self.nodes = []
        self.nodes.append(FakeNode('3MB', '22MB', 2))
        self.nodes.append(FakeNode('8MB', '32MB', 2))
        self.nodes.append(FakeNode('16MB', '32MB', 2))
        self.nodes.append(FakeNode('16MB', '50MB', 1)) # best, but unstable
        self.nodes.append(FakeNode('3MB', '1GB', 2))
    
    def test_filter_less_memory_than(self):
        filtered_nodes = WhitepageSelector._filter_less_memory_than(list(self.nodes), (16,'MB'))
        expected = (self.nodes[2], self.nodes[3])
        self.assertItemsEqual(filtered_nodes, expected)

    def test_select_best_with_infinite_battery(self):        
        selected_node = WhitepageSelector.select_whitepage(self.nodes)
        self.assertEquals(self.nodes[2], selected_node)


if __name__ == '__main__':
    unittest.main()