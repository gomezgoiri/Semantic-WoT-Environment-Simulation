'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from mock import Mock, patch
from netuse.sim_utils import schedule
from SimPy.Simulation import Simulation, Process
from netuse.network_models import DynamicNodesModel

from netuse.nodes import NodeGenerator # used in tested class, here it is patched


class FakeNode(Process):
    
    def __init__(self, sim):
        super(FakeNode, self).__init__(sim=sim)
        self.trace = []
    
    @schedule
    def swap_state(self):
        self.trace.append( self.sim.now() )


class TestDynamicNodesModel(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.nodes = []
        for _ in range(10):
            self.nodes.append( FakeNode( sim=self.simulation ) )
                
        self.random = Mock()
        self.random.normalvariate.side_effect = lambda *args: args[0] - args[1]/2 # just to check how to configure different returns

    def get_nodes(self):
        return self.nodes
    
    @patch.object(NodeGenerator, 'getNodes')
    def test_configure(self, mock_method):
        mock_method.side_effect = self.get_nodes
        
        parametrization = Mock()
        parametrization.simulateUntil = 2000
        
        model = DynamicNodesModel(self.simulation, parametrization, mean=500, std_dev=200)
        model._random = self.random
        
        model.configure() # test method
        self.simulation.simulate(until=parametrization.simulateUntil)
        
        for node in self.get_nodes():
            self.assertItemsEqual( (400, 800, 1200, 1600), node.trace )


if __name__ == '__main__':
    unittest.main()