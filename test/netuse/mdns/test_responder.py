'''
Created on Nov 28, 2011

@author: tulvur
'''

import copy
import unittest
from mock import Mock, patch
from SimPy.Simulation import Simulation
from netuse.mdns.responder import Responder
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord

class TestResponder(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        self.responder = Responder(self.simulation)
                
        self.sample_svr = SVRRecord("name0._http._tcp.local", None, None)
        self.responder.write_record(self.sample_svr)
        
        self.sample_txt = TXTRecord("name0._http._tcp.local", {})
        self.responder.write_record(self.sample_txt)
        
        self.responder._random = Mock()
        self.responder._random.random.side_effect = lambda *args: 0.5 # 0.5 * 2% == 1% of variation
    

    def test_queue_query(self):
        self.simulation.sim = Mock()
        self.simulation.sim.now.side_effect = lambda *args: 0
        
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

if __name__ == '__main__':    
    unittest.main()