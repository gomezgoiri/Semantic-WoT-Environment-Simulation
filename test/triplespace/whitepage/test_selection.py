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
        self.nodes.append(FakeNode('3MB', '22MB', 3))
        self.nodes.append(FakeNode('8MB', '32MB', 2, '1d'))
        self.nodes.append(FakeNode('32MB', '32MB', 2))
        self.nodes.append(FakeNode('34MB', '32MB', 3, '1d'))
        self.nodes.append(FakeNode('16MB', '50MB', 1)) # best, but unstable
        self.nodes.append(FakeNode('3MB', '1GB', 2))
    
    def test_filter_less_memory_than(self):
        filtered_nodes = WhitepageSelector._filter_less_memory_than(list(self.nodes), (16,'MB'))
        expected = (self.nodes[2], self.nodes[3], self.nodes[4])
        self.assertItemsEqual(filtered_nodes, expected)
        
    def test_filter_less_storage_than(self):
        filtered_nodes = WhitepageSelector._filter_less_storage_than(list(self.nodes), 1024*42) # 500 nodes * (1KB * 1024) = at least 42MBs
        expected = (self.nodes[4], self.nodes[5])
        self.assertItemsEqual(filtered_nodes, expected)
    
    def test_any_with_full_battery(self):
        self.assertTrue(self.nodes)
        
        nodes2 = []
        nodes2.append(FakeNode('3MB', '22MB', 2, '2h'))
        nodes2.append(FakeNode('8MB', '32MB', 2, '1d'))
        self.assertFalse(WhitepageSelector._any_with_full_battery(nodes2))
        
    def test_choose_within_full_battery_nodes(self):
        selected_node = WhitepageSelector._choose_within_full_battery_nodes(self.nodes)
        self.assertEquals(self.nodes[2], selected_node)
    
    def test_choose_the_one_with_most_memory(self):
        selected_node = WhitepageSelector._choose_the_one_with_most_memory(self.nodes)
        self.assertEquals(self.nodes[3], selected_node)
        
    def test_filter_unsteady_nodes(self):
        filtered_nodes = WhitepageSelector._filter_unsteady_nodes(list(self.nodes)) # 500 nodes * (1KB * 1024) = at least 42MBs
        expected = (self.nodes[0], self.nodes[1], self.nodes[2], self.nodes[3], self.nodes[5])
        self.assertItemsEqual(filtered_nodes, expected)

    def test_select_whitepage_with_infinite_battery_candidates(self):        
        selected_node = WhitepageSelector.select_whitepage(self.nodes)
        self.assertEquals(self.nodes[2], selected_node)


if __name__ == '__main__':
    unittest.main()