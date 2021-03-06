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

import unittest
from mock import Mock, patch
from SimPy.Simulation import *

from netuse.nodes import Node
from netuse.triplespace.network.client import RequestManager, RequestInstance
from netuse.devices import XBee
from netuse.results import G
from testing.utils import TestingTracer

def side_effect(*args):
    return args[0] + args[1]/2 # just to check how to configure different returns

rndMock = Mock()
rndMock.normalvariate.side_effect = side_effect
#rndMock.normalvariate.return_value = 0

class TestNodes(unittest.TestCase):
    
    #def setUp(self):

    def get_source_node(self):
        source_node = Mock()
        source_node.name = "SourceNode"
        return source_node
    
    def test_request_to_node_down(self):
        G._tracer = TestingTracer()
            
        s = Simulation()
        s.initialize()
        
        node = Node(sim=s, discovery_factory=Mock())
        node.down = True
        s.activate(node, node.processRequests())
        
        req_mngr = RequestManager()
        source_node = self.get_source_node()
        
        request = RequestInstance(source_node, (node,), "/foo/bar", sim=s)
        req_mngr.launchScheduledRequest(request, 10)    
        
        s.simulate(until=3000)
        
        self.assertEquals( 0, len(request.responses) )
        self.assertEquals( 408, G._tracer.traces[0]['status'] )
    
    def test_node_is_not_shown_in_the_discovery_when_is_down(self):
        G._tracer = TestingTracer()
            
        s = Simulation()
        s.initialize()
        
        node = Node(sim=s, discovery_factory=Mock())
        node.down = True
        s.activate(node, node.processRequests())
        
        req_mngr = RequestManager()        
        source_node = self.get_source_node()
        
        request = RequestInstance(source_node, (node,), "/foo/bar", sim=s)
        req_mngr.launchScheduledRequest(request, 10)    
        
        s.simulate(until=3000)
        
        self.assertEquals( 0, len(request.responses) )
        self.assertEquals( 408, G._tracer.traces[0]['status'] )


if __name__ == '__main__':    
    unittest.main()