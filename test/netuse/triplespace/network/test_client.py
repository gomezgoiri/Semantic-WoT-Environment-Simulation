import unittest
from SimPy.Simulation import *
from netuse.triplespace.network.client import RequestManager

class FakeRequestInstance(Process):
    
    def __init__(self, sim=None):
        super(FakeRequestInstance, self).__init__(sim=sim)
        self.when = None
    
    def startup(self):
        self.when = now()
        yield hold, self, 0 # need to be a generator


class RequestManagerTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        initialize()
        self.request = FakeRequestInstance()
    
    def test_NormalRequest(self):
        RequestManager.launchNormalRequest(self.request)
        simulate(100000)
        self.assertEquals(self.request.when, 0)
    
    def test_DelayedRequest(self):
        RequestManager.launchDelayedRequest(self.request, 100)
        simulate(100000)
        self.assertEquals(self.request.when, 100) # after 100 starting in 0
    
    def test_cancel_DelayedRequest(self):
        sq = RequestManager.launchDelayedRequest(self.request, 100)
        RequestManager.cancelRequest(sq)
        simulate(100000)
        self.assertEquals(self.request.when, None)
        
    def test_ScheduledRequest(self):
        RequestManager.launchScheduledRequest(self.request, at=1000)
        simulate(100000)
        self.assertEquals(self.request.when, 1000) # at 1000
    
    def test_cancel_ScheduledRequest(self):
        sq = RequestManager.launchScheduledRequest(self.request, 1000)
        RequestManager.cancelRequest(sq)
        simulate(100000)
        self.assertEquals(self.request.when, None)

if __name__ == '__main__':
    unittest.main()
