'''
Created on Nov 28, 2011

@author: tulvur
'''

import copy
import unittest
from mock import Mock
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
        
        # avoid announcements
        self.node.responder.queued_queries = []
        
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
    
    def count_answers_received_before_all_queries(self, expected_queries):
        counter = 0
        for trace in self.tracer.traces:
            print trace
            if "receiver" in trace:
                counter += 1
            else:
                expected_queries -= 1
                if expected_queries == 0:
                    break
        return counter

    def configure_randomness(self, node, query_randomness, response_randomness):
        node.responder._random = Mock()
        node.responder._random.random.side_effect = lambda *args: response_randomness
        node.browser._random = Mock()
        node.browser._random.random.side_effect = lambda *args: query_randomness

    def create_node(self, name, query_randomness, response_randomness, record):
        node = MDNSNode(name, self.network, self.simulation)
        node.write_record(record)
        node.responder.queued_queries = [] # avoid announcements
        self.configure_randomness( node, query_randomness, response_randomness )
        return node

    def test_network_with_3_nodes_querying_at_the_same_time(self):
        sample_ptr3 = PTRRecord("_http._tcp.local", "name2._http._tcp.local")
        node2 = self.create_node("node2", 0.5001, 0.5, sample_ptr3)
        
        sample_txt4 = TXTRecord("name3._http._tcp.local", {"hello": "world"})
        node3 = self.create_node("node3", 0.5002, 0.5, sample_txt4)
        
        self.configure_randomness( self.node, 0.5, 0.5 )
        
        # first query delayed in the range 20-120ms
        # similar randomness, they will start querying at the same time (more or less)
        # they take the same time to answer (50% of the interval)
        self.node.start()
        node2.start()
        node3.start()
        
        self.simulation.simulate( until=1500 )
        
        # If all the queries are sent first:
        #  + Node A asks: Node B and C send their records using multicast
        #  + Node B asks: Node A sends its record using multicast, Node B using unicast (because the answer was recently sent)
        #  + Node C asks: Node A and Node B send their records using unicast (because the answer was recently sent) 
        self.assertEquals(2, len(self.node.cache.records))
        self.assertEquals(5, len(node2.cache.records))
        self.assertEquals(5, len(node3.cache.records))
        
        self.assertEquals(3, self.count_unicast_communications())


    def test_network_with_3_nodes_at_different_time(self):
        sample_ptr3 = PTRRecord("_http._tcp.local", "name2._http._tcp.local")
        node2 = self.create_node("node2", 0.001, 0.01, sample_ptr3)
        
        sample_txt4 = TXTRecord("name3._http._tcp.local", {"hello": "world"})
        node3 = self.create_node("node3", 0.5, 0.01, sample_txt4)
        
        self.configure_randomness( self.node, 0.99, 0.01 )
        
        # first query delayed in the range 20-120ms
        # different randomness, they will start querying at different moments (more or less)
        # they answer almost immediately (1% of the interval)
        self.node.start()
        node2.start()
        node3.start()
        
        self.simulation.simulate( until=1500 )
        
        # If all the queries are sent first:
        #  + Node A asks: Node B and C send their records using multicast
        #  + Node B asks: Node A sends its record using multicast, no response from Node B's (its records already in known-answers)
        #  + Node C asks: no response (because the answer was recently included in known-answers) 
        self.assertEquals(2, len(self.node.cache.records))
        self.assertEquals(5, len(node2.cache.records))
        self.assertEquals(5, len(node3.cache.records))
        
        self.assertEquals(0, self.count_unicast_communications())


class FakeNetwork(object):
    
    def send_unicast(self, *args):
        self.got = "unicast"
    
    def send_multicast(self, *args):
        self.got = "multicast"


if __name__ == '__main__':    
    unittest.main()