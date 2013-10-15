# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import copy
import unittest
from mock import Mock
from SimPy.Simulation import Simulation
from netuse.mdns.packet import SubQuery
from netuse.mdns.querier import ContinuousQuerier

class FakeSender(object):
    
    WHEN_FIELD = 0
    QUERY_TYPE_FIELD = 1
    SUBQUERY_FIELD = 2
    
    def __init__(self, simulation):
        self.log = []
        self.node_id = "fake"
        self.simulation = simulation
    
    # used by ContinuousQuerier and by self.renew_record
    def send_query(self, subquery, to_node=None): # queries always through multicast
        self.log.append( (self.simulation.now(), "QM" if to_node==None else "QU", subquery) )



class TestCache(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        
        self.browsing_subquery = SubQuery( name = "_services._dns-sd._udp.local",
                                           record_type = "PTR" )
        self.sender = FakeSender(self.simulation) # used for the asserts
        self.querier = ContinuousQuerier(self.browsing_subquery, self.simulation, self.sender)
        
        self.querier._random = Mock()
        self.querier._random.random.side_effect = lambda *args: 0.5
        
        self.simulation.initialize()
        self.simulation.activate(self.querier, self.querier.query_continuously())
    
    def assert_contains_log(self, at, query_type="QM"):
        asserted = False
        for log_line in self.sender.log:
            if log_line[FakeSender.WHEN_FIELD] == at:
                self.assertEquals(query_type, log_line[FakeSender.QUERY_TYPE_FIELD])
                self.assertEquals(self.browsing_subquery, log_line[FakeSender.SUBQUERY_FIELD])
                asserted = True
        self.assertTrue(asserted)
    
    def test_query_continuously_one_query(self):
        self.simulation.simulate( until=20 + 100*0.5 + 1 )
        self.assertEquals(1, len(self.sender.log))
        self.assert_contains_log(20 + 100*0.5, "QU")
    
    def test_query_continuously_two_queries(self):
        self.simulation.simulate( until=20 + 100*0.5 + 1000 + 1 )
        self.assertEquals(2, len(self.sender.log))
        self.assert_contains_log(20 + 100*0.5, "QU")
        self.assert_contains_log(20 + 100*0.5 + 1000, "QM")
    
    def test_query_continuously_three_queries(self):
        self.simulation.simulate( until=20 + 100*0.5 + 1000 + 2000 + 1 )
        self.assertEquals(3, len(self.sender.log))
        self.assert_contains_log(20 + 100*0.5, "QU")
        self.assert_contains_log(20 + 100*0.5 + 1000, "QM")
        self.assert_contains_log(20 + 100*0.5 + 3000, "QM")
    
    def get_time_for_iteration_waiting_1hour(self):
        n = 1 # loops needed to reach to 60mins interval
        interval = 1000
        acum_time = interval
        while interval<3600000:
            interval = interval * 2
            if interval > 3600000: interval = 3600000
            n += 1
            acum_time += interval 
        return acum_time, n
    
    def test_query_continuously_n_queries(self):
        t, n = self.get_time_for_iteration_waiting_1hour()
        self.simulation.simulate( until=20 + 100*0.5 + t + 1 )
        self.assertEquals(n+1, len(self.sender.log)) # +1 for the 1st query!
        self.assert_contains_log(20 + 100*0.5 + t, "QM")
        self.assert_contains_log(20 + 100*0.5 + t - 3600000, "QM")
        

if __name__ == '__main__':    
    unittest.main()