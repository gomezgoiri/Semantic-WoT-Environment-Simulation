import unittest
from mock import Mock, patch
from SimPy.Simulation import Simulation, Process, hold, passivate
from netuse.sim_utils import activatable
from netuse.triplespace.network.client import RequestManager, RequestInstance

class FakeRequestInstance(Process):
    
    def __init__(self, sim=None):
        super(FakeRequestInstance, self).__init__( sim = sim, name = "Fake request" )
        self.when = None
    
    def startup(self):
        self.when = self.sim.now()
        yield hold, self, 0 # need to be a generator


class RequestManagerTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.s = Simulation()
        self.s.initialize()
        self.request = FakeRequestInstance(sim=self.s)
    
    def test_NormalRequest(self):
        RequestManager.launchNormalRequest(self.request)
        self.s.simulate(100000)
        self.assertEquals(0, self.request.when)
    
    def test_DelayedRequest(self):
        RequestManager.launchDelayedRequest(self.request, 100)
        self.s.simulate(100000)
        self.assertEquals(100, self.request.when) # after 100 starting in 0
    
    def test_cancel_DelayedRequest(self):
        RequestManager.launchDelayedRequest(self.request, 100)
        RequestManager.cancelRequest(self.request)
        self.s.simulate(100000)
        self.assertEquals(None, self.request.when)
        
    def test_ScheduledRequest(self):
        RequestManager.launchScheduledRequest(self.request, at=1000)
        self.s.simulate(100000)
        self.assertEquals(1000, self.request.when) # at 1000
    
    def test_cancel_ScheduledRequest(self):
        RequestManager.launchScheduledRequest(self.request, 1000)
        RequestManager.cancelRequest(self.request)
        self.s.simulate(100000)
        self.assertEquals(None, self.request.when)


class FakeAvailableNode(Process):
    
    def __init__(self, name, sim):
        super(FakeAvailableNode, self).__init__(name=name, sim=sim)
        self.__httpIn = []
    
    def queueRequest(self, requester, req):
        self.__httpIn.append( (requester, req) )
        self.sim.reactivate(self) # starts answering
        
    @activatable
    def processRequests(self):
        while 1:
            if not self.__httpIn: # if it's empty...
                yield passivate, self
            else:
                requester, request = self.__httpIn[0]
                response = Mock()
                response.getid.return_value = request.getid()
                requester.addResponse(response)
                del self.__httpIn[0]


class RequestInstanceTestCase(unittest.TestCase):

    def setUp(self):
        self.s = Simulation()
        self.s.initialize()
    
    def get_me(self):
        me = Mock()
        me.name = "origin"
        return me
    
    def get_unavailable_node(self, name):
        node = Mock()
        node.queueRequest.return_value = None
        node.name = name
        return node
    
    def get_available_node(self, name):
        n = FakeAvailableNode(name, self.s)
        n.processRequests(at=0)
        return n
    
    @patch('netuse.results.G._tracer', Mock()) # new global unrandomized variable 
    def test_get_unanswered_nodes(self):
        nodes = []
        nodes.append( self.get_available_node("aval1") )
        nodes.append( self.get_unavailable_node("unaval") )
        nodes.append( self.get_available_node("aval2") )
        me = self.get_me() # otherwise weakref of RequestInstance will delete it
        
        ri = RequestInstance(me, nodes, "/fakeurl", sim=self.s)
        RequestManager.launchNormalRequest(ri)
        self.s.simulate(100000)
        
        unanswered = ri.get_unanswered_nodes()
        self.assertTrue( nodes[1].name in unanswered )
        self.assertFalse( nodes[0].name in unanswered )
        self.assertFalse( nodes[2].name in unanswered )


if __name__ == '__main__':
    unittest.main()