import unittest
import random
from mock import Mock
from netuse.triplespace.network.discovery.simple import MagicInstantNetwork, SimpleDiscoveryMechanism


class SimpleDiscoveryMechanismTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def _get_mock_node_and_record(self, name):
        node = Mock()
        node.name = name
        node.down = False
        discovery_record = Mock()
        discovery_record.add_change_observer.return_value = None
        discovery_record.is_whitepage = False
        discovery_record.node_name = name
        return node, discovery_record

    def setUp(self):
        nodes = {}
        
        self.main_node, self.main_record = self._get_mock_node_and_record("main_node")
        nodes[self.main_node.name] = self.main_node
        
        self.other_records = []
        for i in range(10):
            node, record = self._get_mock_node_and_record("node_%d"%(i))
            nodes[node.name] = node
            self.other_records.append(record)
        
        get_node_for_record = Mock()
        get_node_for_record.side_effect = lambda record: None if record is None else nodes[record.node_name]
        
        self.network = MagicInstantNetwork()
        self.network._get_node_for_record = get_node_for_record
        
        self.simple_discovery = SimpleDiscoveryMechanism(self.main_record, self.network)
        self.simple_discovery._get_node_for_record = get_node_for_record
        
        for record in self.other_records:
            fake_discovery_instance = Mock()
            fake_discovery_instance.get_my_record.return_value = record
            self.network.join_space(fake_discovery_instance)
    
    def test_get_discovered_records(self):
        records = self.simple_discovery.get_discovered_records()
        self.assertEquals( 10, len(records) )
        self.assertFalse( self.main_record in records )
        for record in records:
            self.assertTrue( record in self.other_records )
    
    def test_get_discovered_records_from_down_node(self):
        self.main_node.down = True
        nodes = self.simple_discovery.get_discovered_records()
        self.assertEquals( 0, len(nodes) )
        
    def test_get_discovered_records_in_network_with_down_nodes(self):
        down_nodes = []
        for record in self.other_records:
            node = self.simple_discovery._get_node_for_record(record)
            node.down = True
            down_nodes.append(node)
            if len(down_nodes)>=5:
                break
        
        records = self.simple_discovery.get_discovered_records()
        
        self.assertEquals( 5, len(records) )
        self.assertFalse( self.main_record in records )
        for record in records:
            node = self.simple_discovery._get_node_for_record(record)
            self.assertFalse( node in down_nodes )
            self.assertTrue( record in self.other_records )
            
    def test_get_no_whitepage(self):
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(None, wp)
    
    def test_get_whitepage_me(self):
        self.main_record.is_whitepage = True
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(self.main_node, wp)
    
    def test_get_whitepage_others(self):
        expected_wp_rec = random.choice(self.other_records)
        expected_wp_rec.is_whitepage = True
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(self.simple_discovery._get_node_for_record(expected_wp_rec), wp)


if __name__ == '__main__':
    unittest.main()