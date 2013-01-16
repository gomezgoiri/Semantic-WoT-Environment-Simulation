import unittest
import urllib
from mock import Mock
from rdflib import URIRef
from rdflib.Literal import Literal, _XSD_NS
from netuse.nodes import Node
from netuse.devices import DeviceType, XBee, SamsungGalaxyTab, FoxG20, Server
from netuse.triplespace.network.discovery.record import DiscoveryRecord
from netuse.triplespace.our_solution.whitepage.selection import WhitepageSelector


class TestRecord(DiscoveryRecord):
    
    def __init__(self, memory='1MB', storage='1MB',
                 joined_since=1, battery_lifetime=DiscoveryRecord.INFINITE_BATTERY, sac=False, is_whitepage=False):
        super(TestRecord, self).__init__("fake_node_name", memory, storage, joined_since, sac, battery_lifetime)
    
    def tuple_to_str(self, tuple):
        return str(tuple[0]) + tuple[1]
    
    def __repr__(self):
        return "(" + self.tuple_to_str(self.discovery_record.memory) + ", " + self.tuple_to_str(self.discovery_record.storage) + ", " + self.discovery_record.battery_lifetime + ")"


class WhitepageSelectorTestCase(unittest.TestCase):
    
    def setUp(self):
        self.record = []
        self.record.append(TestRecord('3MB', '22MB', 3))
        self.record.append(TestRecord('8MB', '32MB', 2, '1d'))
        self.record.append(TestRecord('32MB', '32MB', 2))
        self.record.append(TestRecord('34MB', '32MB', 3, '1d'))
        self.record.append(TestRecord('16MB', '50MB', 1)) # best, but unstable
        self.record.append(TestRecord('3MB', '1GB', 2))
    
    def test_filter_less_memory_than(self):
        filtered_records = WhitepageSelector._filter_less_memory_than(list(self.record), (16,'MB'))
        expected = (self.record[2], self.record[3], self.record[4])
        self.assertItemsEqual(filtered_records, expected)
        
    def test_filter_less_storage_than(self):
        filtered_records = WhitepageSelector._filter_less_storage_than(list(self.record), 1024*42) # 500 record * (1KB * 1024) = at least 42MBs
        expected = (self.record[4], self.record[5])
        self.assertItemsEqual(filtered_records, expected)
    
    def test_any_with_full_battery(self):
        self.assertTrue(self.record)
        
        records2 = []
        records2.append(TestRecord('3MB', '22MB', 2, '2h'))
        records2.append(TestRecord('8MB', '32MB', 2, '1d'))
        self.assertFalse(WhitepageSelector._any_with_full_battery(records2))
        
    def test_choose_within_full_battery_nodes(self):
        selected_record = WhitepageSelector._choose_within_full_battery_nodes(self.record)
        self.assertEquals(self.record[2], selected_record)
    
    def test_choose_the_one_with_most_memory(self):
        selected_record = WhitepageSelector._choose_the_one_with_most_memory(self.record)
        self.assertEquals(self.record[3], selected_record)
        
    def test_filter_unsteady_nodes(self):
        filtered_records = WhitepageSelector._filter_unsteady_nodes(list(self.record)) # 500 record * (1KB * 1024) = at least 42MBs
        expected = (self.record[0], self.record[3])
        self.assertItemsEqual(filtered_records, expected)

    def test_select_whitepage_with_infinite_battery_candidates(self):        
        selected_record = WhitepageSelector.select_whitepage(self.record)
        self.assertEquals(self.record[2], selected_record)
        
    def test_select_with_real_devices(self):
        candidates = []
        
        factory = Mock()
        factory.create_simple_discovery.side_effect = lambda node, record: candidates.append(record)
        
        for _ in range(1): Node("server", discovery_factory = factory, device = DeviceType.create(Server.TYPE_ID))
        for i in range(30): Node("galaxy_%d"%(i), discovery_factory = factory, device = DeviceType.create(SamsungGalaxyTab.TYPE_ID))
        for i in range(69): Node("fox_%d"%(i), discovery_factory = factory, device = DeviceType.create(FoxG20.TYPE_ID))
        for i in range(200): Node("xbee_%d"%(i), discovery_factory = factory, device = DeviceType.create(XBee.TYPE_ID))
        
        selected_record = WhitepageSelector.select_whitepage(candidates)
        self.assertEquals("server", selected_record.node_name)


if __name__ == '__main__':
    unittest.main()