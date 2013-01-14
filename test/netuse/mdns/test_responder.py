'''
Created on Nov 28, 2011

@author: tulvur
'''

import copy
import unittest
from mock import Mock, patch
from SimPy.Simulation import Simulation
from netuse.mdns.responder import Responder
from netuse.mdns.packet import Query, SubQuery
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord

class TestResponder(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        self.responder = Responder(self.simulation)
        
        self.sample_ptr = PTRRecord("_http._tcp.local", "name0._http._tcp.local")
        self.responder.write_record(self.sample_ptr)
        
        self.sample_svr = SVRRecord("name0._http._tcp.local", None, None)
        self.responder.write_record(self.sample_svr)
        
        self.sample_txt = TXTRecord("name0._http._tcp.local", {})
        self.responder.write_record(self.sample_txt)
        
        self.sample_ptr2 = PTRRecord("_app._udp.local", "instance1._app._udp.local")
        self.responder.write_record(self.sample_ptr2)
        
        self.responder._random = Mock()
        self.responder._random.random.side_effect = lambda *args: 0.5 # 0.5 * 2% == 1% of variation
    

    def test_queue_query(self):
        self.responder.sim = Mock()
        self.responder.sim.now.side_effect = lambda *args: 0
        
        query = Mock()
        query.response_is_unique.side_effect = lambda *args: True
        self.responder.queue_query(query)
        
        self.assertEquals(1, len(self.responder.queued_queries))
        self.assertEquals(5.0, self.responder.queued_queries[0][0]) # at 5ms (between 0-10ms)
        self.assertEquals(query, self.responder.queued_queries[0][1])
        
        query2 = Mock()
        query2.response_is_unique.side_effect = lambda *args: False
        self.responder.queue_query(query2)
        
        self.assertEquals(2, len(self.responder.queued_queries))
        self.assertEquals(70.0, self.responder.queued_queries[1][0]) # at 70ms (between 20-120ms)
        self.assertEquals(query2, self.responder.queued_queries[1][1])
    
    def test_get_possible_answers_txt_query(self):
        sq = SubQuery("name0._http._tcp.local", "TXT")
        q = Query((sq,))
        
        responses = self.responder._get_possible_answers(q)
        self.assertEquals(1, len(responses))
        self.assertTrue(self.sample_txt in responses)
        
    def test_get_possible_answers_ptr_http_query(self):
        sq = SubQuery("_http._tcp.local", "PTR")
        q = Query((sq,))
        
        responses = self.responder._get_possible_answers(q)
        self.assertEquals(3, len(responses))
        self.assertTrue(self.sample_ptr in responses)
        self.assertTrue(self.sample_svr in responses)
        self.assertTrue(self.sample_txt in responses)
        
    def test_get_possible_answers_ptr_all_query(self):
        sq = SubQuery("_services._dns-sd._udp.local", "PTR")
        q = Query((sq,))
        
        responses = self.responder._get_possible_answers(q)
        self.assertEquals(4, len(responses))
        self.assertTrue(self.sample_ptr in responses)
        self.assertTrue(self.sample_svr in responses)
        self.assertTrue(self.sample_txt in responses)
        self.assertTrue(self.sample_ptr2 in responses)
    
    def test_get_possible_answers_ptr_multiple_query(self):
        sq1 = SubQuery("name0._http._tcp.local", "TXT")
        sq2 = SubQuery("name0._http._tcp.local", "SVR")
        q = Query((sq1, sq2))
        
        responses = self.responder._get_possible_answers(q)
        self.assertEquals(2, len(responses))
        self.assertTrue(self.sample_txt in responses)
        self.assertTrue(self.sample_svr in responses)
        
    def test_suppress_known_answers(self):
        q = Query(None, known_answers=(self.sample_txt, self.sample_ptr2))
        possible_answers = [self.sample_ptr, self.sample_ptr2, self.sample_txt, self.sample_svr]
        
        self.responder._suppress_known_answers(q, possible_answers)
        self.assertEquals(2, len(possible_answers))
        self.assertTrue(self.sample_ptr in possible_answers)
        self.assertTrue(self.sample_svr in possible_answers)
    
    def test_send_using_proper_method_qm(self):
        fn = FakeNetwork()
        self.responder.sender = fn
        self.responder._send_using_proper_method( Query(None), None )
        self.assertEquals("multicast", fn.got)
        
    def test_send_using_proper_method_qu_never_sent_before(self):
        self.responder.sim = Mock()
        self.responder.sim.now.side_effect = lambda *args: 0
        
        fn = FakeNetwork()
        self.responder.sender = fn
        self.responder._send_using_proper_method( Query(None, to_node="fake_id"), (self.sample_txt,) )
        self.assertEquals("multicast", fn.got)
                
    def test_send_using_proper_method_qu_not_sent_lately(self):
        self.responder.sim = Mock()
        # 25% of 75 mins of TTL of the TXT record + 1 ms
        self.responder.sim.now.side_effect = lambda *args: 75 * 60 * 1000 * 0.25 + 1
        self.responder.local_records[self.sample_txt] = 0
        
        fn = FakeNetwork()
        self.responder.sender = fn
        self.responder._send_using_proper_method( Query(None, to_node="fake_id"), (self.sample_txt,) )
        self.assertEquals("multicast", fn.got)
        
    def test_send_using_proper_method_qu_sent_lately(self):
        self.responder.sim = Mock()
        # 25% of 75 mins of TTL of the TXT record - 1 ms
        self.responder.sim.now.side_effect = lambda *args: 75 * 60 * 1000 * 0.25 - 1
        self.responder.local_records[self.sample_txt] = 0
        
        fn = FakeNetwork()
        self.responder.sender = fn
        self.responder._send_using_proper_method( Query(None, to_node="fake_id"), (self.sample_txt,) )
        self.assertEquals("unicast", fn.got)



class FakeNetwork(object):
    
    def send_unicast(self, *args):
        self.got = "unicast"
    
    def send_multicast(self, *args):
        self.got = "multicast"


if __name__ == '__main__':    
    unittest.main()