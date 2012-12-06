import unittest
from SimPy.Simulation import Simulation, Process, waitevent
from netuse.sim_utils import schedule, Timer

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


class ObjectWhichUsesTimer(Process):
    
    def __init__(self, timeToWait, sim):
        super(ObjectWhichUsesTimer, self).__init__(sim=sim)
        self.time_after_waiting = 0
        self.timer = Timer(waitUntil=timeToWait, sim=sim)
        
    def do_whatever_you_do_in_simulation(self):
        self.sim.activate(self.timer, self.timer.wait())#, self.__maxWaitingTime)
        while not self.timer.ended:
            yield waitevent, self, (self.timer.event,)
        self.time_after_waiting = self.sim.now()

class TimerTestCase(unittest.TestCase):

    def test_wait(self):        
        s = Simulation()
        s.initialize()
        
        obj = ObjectWhichUsesTimer(timeToWait=10, sim=s)
        s.activate(obj, obj.do_whatever_you_do_in_simulation())
        
        s.simulate(until=300)
        self.assertEquals(10, obj.time_after_waiting)

if __name__ == '__main__':
    unittest.main()
