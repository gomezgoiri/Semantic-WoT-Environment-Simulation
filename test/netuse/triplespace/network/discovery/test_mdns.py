import unittest
import random
from clueseval.clues.versions.management import Version
from netuse.triplespace.network.discovery.mdns import DiscoveryRecordConverter
from netuse.mdns.record import TXTRecord
from netuse.triplespace.network.discovery.record import DiscoveryRecord

class DiscoveryRecordConverterTestCase(unittest.TestCase):
    
    def setUp(self):
        self.record1_txt = TXTRecord(
                                "name0._http._tcp.local",
                                keyvalues = {'js': 12, 'bl': 13, 'iw': True, 'm': '64MB', 's': '2GB' }
                            )
        self.record1_dr = DiscoveryRecord(
                                "name0",
                                memory = '64MB',
                                storage = '2GB',
                                joined_since = 12,
                                battery_lifetime = 13,
                                is_whitepage = True
                            )
        
        self.record2_txt = TXTRecord(
                                "name1._http._tcp.local",
                                keyvalues = {'js': 20, 'bl': 21, 'iw': False, 'm': '32MB', 's': '4GB', 'g': 10, 'v': 20 }
                            )
        self.record2_dr = DiscoveryRecord(
                                "name1",
                                memory = '32MB',
                                storage = '4GB',
                                joined_since = 20,
                                battery_lifetime = 21,
                                is_whitepage = False )
        self.record2_dr.version = Version( generation = 10, version = 20 )
    
    def test_to_txt_record(self):
        got = DiscoveryRecordConverter.to_txt_record(self.record1_dr)
        
        self.assertEquals(self.record1_txt, got) # because it is redefined in TXTRecord
        self.assertNotEquals(self.record2_txt, got)
        
        self.assertEquals(self.record1_txt.keyvalues, got.keyvalues)
        self.assertNotEquals(self.record2_txt.keyvalues, got.keyvalues)
        
        
        got = DiscoveryRecordConverter.to_txt_record(self.record2_dr)
        
        self.assertNotEquals(self.record1_txt, got) # because it is redefined in TXTRecord
        self.assertEquals(self.record2_txt, got)
        
        self.assertNotEquals(self.record1_txt.keyvalues, got.keyvalues)
        self.assertEquals(self.record2_txt.keyvalues, got.keyvalues)
    
    def assert_discovery_record_equals(self, expected, got):
        self.assertEquals(expected.node_name, got.node_name)
        self.assertEquals(expected.memory, got.memory)
        self.assertEquals(expected.storage, got.storage)
        self.assertEquals(expected.joined_since, got.joined_since)
        self.assertEquals(expected.battery_lifetime, got.battery_lifetime)
        self.assertEquals(expected.is_whitepage, got.is_whitepage)
    
    def test_to_discovery_record(self):
        got = DiscoveryRecordConverter.to_discovery_record(self.record1_txt)
        self.assert_discovery_record_equals(self.record1_dr, got)
        try:
            self.assert_discovery_record_equals(self.record2_dr, got)
            self.fail()
        except:
            pass
        
        got = DiscoveryRecordConverter.to_discovery_record(self.record2_txt)
        self.assert_discovery_record_equals(self.record2_dr, got)
        try:
            self.assert_discovery_record_equals(self.record1_dr, got)
            self.fail()
        except:
            pass


if __name__ == '__main__':
    unittest.main()