import unittest
import random
from mock import Mock
from netuse.triplespace.network.discovery.simple import MagicInstantNetwork, SimpleDiscoveryMechanism


class SimpleDiscoveryMechanismTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def _get_mock_node(self, name):
        node = Mock()
        node.name = name
        node.discovery_record = Mock()
        node.discovery_record.add_change_observer.return_value = None
        node.discovery_record.is_whitepage = False
        node.down = False
        return node

    def setUp(self):
        nodes = []
        
        self.main_node = self._get_mock_node("main_node")
        nodes.append(self.main_node)
        
        self.other_nodes = []
        for i in range(10):
            node = self._get_mock_node("node_%d"%(i))
            nodes.append(node)
            self.other_nodes.append(node)
        
        self.network = MagicInstantNetwork(nodes)
        self.simple_discovery = SimpleDiscoveryMechanism(self.main_node, self.main_node.discovery_record, self.network)
    
    def test_get_nodes(self):
        nodes = self.simple_discovery.get_nodes()
        self.assertEquals( 10, len(nodes) )
        self.assertFalse( self.main_node in nodes )
        for node in nodes:
            self.assertTrue( node in self.other_nodes )
    
    def test_get_nodes_from_down_node(self):
        self.main_node.down = True
        nodes = self.simple_discovery.get_nodes()
        self.assertEquals( 0, len(nodes) )
        
    def test_get_nodes_in_network_with_down_nodes(self):
        down_nodes = []
        for node in self.other_nodes:
            node.down = True
            down_nodes.append(node)
            if len(down_nodes)>=5:
                break
        
        nodes = self.simple_discovery.get_nodes()
        
        self.assertEquals( 5, len(nodes) )
        self.assertFalse( self.main_node in nodes )
        for node in down_nodes:
            self.assertFalse( node in nodes )
        for node in nodes:
            self.assertTrue( node in self.other_nodes )
            
    def test_get_no_whitepage(self):
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(None, wp)
    
    def test_get_whitepage_me(self):
        self.main_node.discovery_record.is_whitepage = True
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(self.main_node, wp)
    
    def test_get_whitepage_others(self):
        expected_wp = random.choice(self.other_nodes)
        expected_wp.discovery_record.is_whitepage = True
        wp = self.simple_discovery.get_whitepage()
        self.assertEquals(expected_wp, wp)

if __name__ == '__main__':
    unittest.main()