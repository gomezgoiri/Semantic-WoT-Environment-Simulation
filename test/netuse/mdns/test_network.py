'''
Created on Nov 28, 2011

@author: tulvur
'''

import copy
import unittest
from mock import Mock, patch
from SimPy.Simulation import Simulation
from netuse.mdns.network import UDPNetwork, MDNSNode
from netuse.mdns.responder import Responder
from netuse.mdns.packet import Query, SubQuery
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord
from testing.utils import TestingTracer


class TestResponder(unittest.TestCase):
    
    def setUp(self):
        self.tracer = TestingTracer()
        self.simulation = Simulation()
        
        self.network = UDPNetwork( self.simulation, udp_tracer = self.tracer )
        self.node = MDNSNode("node0", self.network, self.simulation)
        
        self.sample_ptr = PTRRecord("_http._tcp.local", "name0._http._tcp.local")
        self.node.write_record(self.sample_ptr)
        
        self.sample_svr = SVRRecord("name0._http._tcp.local", None, None)
        self.node.write_record(self.sample_svr)
        
        self.sample_txt = TXTRecord("name0._http._tcp.local", {})
        self.node.write_record(self.sample_txt)
        
        self.sample_ptr2 = PTRRecord("_app._udp.local", "instance1._app._udp.local")
        self.node.write_record(self.sample_ptr2)
        
        self.simulation.initialize()
    

    def test_network_with_2_nodes(self):
        node2 = MDNSNode("node2", self.network, self.simulation)
        sample_ptr3 = PTRRecord("_http._tcp.local", "name2._http._tcp.local")
        node2.write_record(sample_ptr3)
        
        self.node.start()
        node2.start()
        
        self.simulation.simulate( until=1500 )
        
        self.assertEquals(1, len(self.node.cache.records))
        self.assertEquals(4, len(node2.cache.records))
    
    def count_unicast_communications(self):
        counter = 0
        for trace in self.tracer.traces:
            if "receiver" in trace and trace["receiver"]!="all":
                counter += 1
        return counter

    def test_network_with_3_nodes(self):
        node2 = MDNSNode("node2", self.network, self.simulation)
        sample_ptr3 = PTRRecord("_http._tcp.local", "name2._http._tcp.local")
        node2.write_record(sample_ptr3)
        
        node3 = MDNSNode("node3", self.network, self.simulation)
        sample_txt4 = TXTRecord("name3._http._tcp.local", {"hello": "world"})
        node3.write_record(sample_txt4)
        
        self.node.start()
        node2.start()
        node3.start()
        
        self.simulation.simulate( until=1500 )
        
        self.assertEquals(2, len(self.node.cache.records))
        self.assertEquals(5, len(node2.cache.records))
        self.assertEquals(5, len(node3.cache.records))
        
        # Node A asks: Node B and C send their records using multicast
        # Node B asks: Node A sends its record using multicast, Node B using unicast (because the answer was recently sent)
        # Node C asks: Node A and Node B send their records using unicast (because the answer was recently sent) 
        self.assertEquals(3, self.count_unicast_communications())

class FakeNetwork(object):
    
    def send_unicast(self, *args):
        self.got = "unicast"
    
    def send_multicast(self, *args):
        self.got = "multicast"


if __name__ == '__main__':    
    unittest.main()