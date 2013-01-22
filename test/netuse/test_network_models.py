'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from mock import Mock, patch
from netuse.sim_utils import schedule
from SimPy.Simulation import Simulation, Process
from netuse.network_models import DynamicNodesModel, OneNodeDownModel, ChaoticModel

from netuse.nodes import NodeManager # used in tested class, here it is patched


class FakeNode(Process):
    
    def __init__(self, sim):
        super(FakeNode, self).__init__(sim=sim)
        self.trace = []
        self.state = "up"
    
    @schedule
    def swap_state(self):
        self.state = "down" if self.state is "up" else "up"
        self.trace.append( (self.sim.now(), self.state) )


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
    
    @patch.object(NodeManager, 'getNodes')
    def test_configure(self, mock_method):
        mock_method.side_effect = self.get_nodes
        
        simulateUntil = 2000
        
        model = DynamicNodesModel(simulateUntil, 500, 200)
        model._random = self.random
                
        model.configure() # test method
        self.simulation.simulate(until=simulateUntil)
        
        for node in self.get_nodes():
            self.assertItemsEqual( ( (400, "down"),
                                     (800, "up"),
                                     (1200, "down"),
                                     (1600, "up") ), node.trace )


class TestOneNodeDownModel(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.nodes = []
        for _ in range(10):
            self.nodes.append( FakeNode( sim=self.simulation ) )
        
        self.random = Mock()
        self.random.normalvariate.side_effect = lambda *args: args[0] - args[1]/2 # just to check how to configure different returns
        import random
        self.random.choice.side_effect = random.choice # otherwise choice method will be mocked!

    def get_nodes(self):
        return self.nodes
    
    @patch.object(NodeManager, 'getNodes')
    def test_configure(self, mock_method):
        mock_method.side_effect = self.get_nodes
        
        simulateUntil = 2000
        
        model = OneNodeDownModel(simulateUntil, 500, 200)
        model._random = self.random
        
        model.configure() # test method
        self.simulation.simulate(until=simulateUntil)
        
        total_activity = [ (400, "down"), (800, "up"),
                           (800, "down"), (1200, "up"),
                           (1200, "down"), (1600, "up"),
                           (1600, "down"), ]
        
        for node in self.get_nodes():
            for trace in node.trace:
                self.assertTrue( trace in total_activity )
                if trace[1] is "down" and trace[0]<1600:
                    # if the node goes down, in 400 ms should go up again
                    self.assertTrue( (trace[0]+400, "up") in node.trace )
                
                total_activity.remove(trace)
        
        # all the traces should have been conveniently removed in the previous for
        self.assertEquals(0, len(total_activity))


class TestChaoticModel(unittest.TestCase):
    
    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.nodes = []
        for _ in range(10):
            self.nodes.append( FakeNode( sim=self.simulation ) )
        
        self.random = Mock()
        self.random.normalvariate.side_effect = lambda *args: args[0] - args[1]/2 # just to check how to configure different returns
    
    def _get_node_for_record(self, record):
        print record
    
    def patch_find_whitepage(self, model):
        model.find_whitepage = Mock()
        model.find_whitepage.return_value = self.nodes[0] # select the first as WP
    
    def test_run(self):
        model = ChaoticModel(self.simulation, 500, 200)
        model._random = self.random
        self.patch_find_whitepage(model)
        
        model.run(at=0) # test method
        self.simulation.simulate(until=2000)
        
        # WP from the previous loop goes up, current WP goes down
        # In this case the WP is always the same
        self.assertItemsEqual( ( (400, "down"),
                                 (800, "up"), (800, "down"),
                                 (1200, "up"), (1200, "down"),
                                 (1600, "up"), (1600, "down"),
                                 (2000, "up"), (2000, "down") ), self.nodes[0].trace )
        
        for n in range( 1, len(self.nodes) ):
            self.assertEquals( 0, len(self.nodes[n].trace) )


if __name__ == '__main__':
    unittest.main()