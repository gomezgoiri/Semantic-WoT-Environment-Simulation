import unittest
from SimPy.Simulation import Simulation
from netuse.sim_utils import schedule

class FakeClass(object):
    
    def __init__(self, simulation):
        self.simulation = simulation
    
    @schedule
    def function1(self):
        return self.simulation.now()
    
    @schedule
    def function2(self, str_param):
        return (self.simulation.now(), str_param)

class RequestManagerTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.fc = FakeClass(self.simulation)
        
    def test_scheduled_function1(self):
        r = self.fc.function1(starts_at=100, simulation=self.simulation) # or directly: r = self.fc.function1(100)
        self.simulation.simulate(100000)
        self.assertEquals(r.get_result(), 100)
    
    def test_scheduled_function2(self):
        r = self.fc.function2(starts_at=200, simulation=self.simulation, str_param="helloworld")
        self.simulation.simulate(100000)
        self.assertEquals(r.get_result(), (200, "helloworld"))

if __name__ == '__main__':
    unittest.main()
