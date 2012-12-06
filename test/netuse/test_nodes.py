'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from mock import Mock, patch
from SimPy.Simulation import *

from netuse.nodes import Node
from netuse.triplespace.network.client import RequestManager, RequestInstance
from netuse.devices import XBee

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
    
    #@patch('netuse.results.G.Rnd', rndMock) # new global unrandomized variable 
    def test_node_down(self):        
        s = Simulation()
        s.initialize()
        
        node = Node(sim=s)
        node.down = True
        s.activate(node, node.processRequests())
        
        req_mngr = RequestManager()        
        source_node = self.get_source_node()
        
        request = RequestInstance(source_node, (node,), "/foo/bar", sim=s)
        req_mngr.launchScheduledRequest(request, 10)    
        
        s.simulate(until=3000)
        
        print request.responses[0].getstatus()


if __name__ == '__main__':    
    unittest.main()