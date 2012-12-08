import unittest
from mock import Mock
from SimPy.Simulation import Simulation, Process, hold
from netuse.triplespace.network.discovery.simple import MagicInstantNetwork, SimpleDiscoveryMechanism


class SimpleDiscoveryMechanismTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def _get_mock_node(self, name):
        node = Mock()
        node.name = name
        node.discovery_record = Mock()
        node.discovery_record.add_change_observer.return_value = None
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
        self.simple_discovery = SimpleDiscoveryMechanism(self.main_node, self.network)
    
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

if __name__ == '__main__':
    unittest.main()