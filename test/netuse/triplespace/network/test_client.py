import unittest
from SimPy.Simulation import Simulation, Process, hold
from netuse.triplespace.network.client import RequestManager

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
        self.assertEquals(self.request.when, 0)
    
    def test_DelayedRequest(self):
        RequestManager.launchDelayedRequest(self.request, 100)
        self.s.simulate(100000)
        self.assertEquals(self.request.when, 100) # after 100 starting in 0
    
    def test_cancel_DelayedRequest(self):
        RequestManager.launchDelayedRequest(self.request, 100)
        RequestManager.cancelRequest(self.request)
        self.s.simulate(100000)
        self.assertEquals(self.request.when, None)
        
    def test_ScheduledRequest(self):
        RequestManager.launchScheduledRequest(self.request, at=1000)
        self.s.simulate(100000)
        self.assertEquals(self.request.when, 1000) # at 1000
    
    def test_cancel_ScheduledRequest(self):
        RequestManager.launchScheduledRequest(self.request, 1000)
        RequestManager.cancelRequest(self.request)
        self.s.simulate(100000)
        self.assertEquals(self.request.when, None)

if __name__ == '__main__':
    unittest.main()