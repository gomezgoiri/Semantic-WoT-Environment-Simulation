import unittest
from SimPy.Simulation import *
from netuse.sim_utils import schedule

class FakeClass(object):
    
    def __init__(self):
        pass
    
    @schedule
    def function1(self):
        return now()
    
    @schedule
    def function2(self, str_param):
        return (now(), str_param)

class RequestManagerTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.fc = FakeClass()
        initialize()
        
    def test_scheduled_function1(self):
        r = self.fc.function1(starts_at=100) # or directly: r = self.fc.function1(100)
        simulate(100000)
        self.assertEquals(r.get_result(), 100)
    
    def test_scheduled_function2(self):
        r = self.fc.function2(starts_at=200, str_param="helloworld")
        simulate(100000)
        self.assertEquals(r.get_result(), (200, "helloworld"))

if __name__ == '__main__':
    unittest.main()
