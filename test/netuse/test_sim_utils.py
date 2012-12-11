import unittest
from SimPy.Simulation import Simulation, Process, waitevent, hold
from netuse.sim_utils import schedule, activatable, Timer

class SimpleProcess(Process):
    
    def __init__(self, sim):
        super(SimpleProcess, self).__init__(sim=sim)
        self.traces = []
    
    @activatable
    def method_without_parameters(self):
        yield hold, self, 0
        self.traces.append( ("method1", self.sim.now()) )
    
    @activatable
    def method_with_parameters(self, str_param):
        yield hold, self, 0
        self.traces.append( ("method2", self.sim.now(), str_param) )
        
    @activatable
    def not_generator(self):
        pass


class ActivatableTestCase(unittest.TestCase): # wrapper under test: activatable

    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.proc1 = SimpleProcess(sim=self.simulation)
        self.proc2 = SimpleProcess(sim=self.simulation)
        
    def test_exception_not_generator(self):
        self.proc1 = SimpleProcess(sim=self.simulation)
        try:
            self.proc1.not_generator(at=300)
            self.fail()
        except Exception, e:
            #print e
            pass
    
    def test_scheduled_method_without_parameters(self):
        self.proc1.method_without_parameters(at=100)
        self.proc1.method_without_parameters(at=300) # the second activation for a given object is ignored
        self.proc2.method_without_parameters(at=500)
        
        self.simulation.simulate(10000)
        
        self.assertItemsEqual( ( ("method1", 100), ), self.proc1.traces)
        self.assertItemsEqual( ( ("method1", 500),  ), self.proc2.traces)
    
    def test_scheduled_method_with_parameters(self):
        self.proc1.method_with_parameters(at=500, str_param="gato")
        self.proc1.method_with_parameters(at=300, str_param="perro") # the second activation for a given object is ignored
        self.proc2.method_with_parameters(at=100, str_param="iguana")
        
        self.simulation.simulate(10000)
        
        self.assertItemsEqual( ( ("method2", 500, "gato"), ), self.proc1.traces)
        self.assertItemsEqual( ( ("method2", 100, "iguana"),  ), self.proc2.traces)
    
    def test_scheduled_methods_all(self):
        self.proc1.method_with_parameters(at=400, str_param="armadillo")
        self.proc1.method_without_parameters(at=300)  # the second activation for a given object is ignored, even if it is a different method
        
        self.simulation.simulate(10000)
        
        self.assertItemsEqual( ( ("method2", 400, "armadillo"), ), self.proc1.traces)


class FakeClass(object):
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.traces = [] # to test multiple scheduled calls
    
    @schedule
    def method1(self): # without parameters
        self.traces.append( ("method1", self.simulation.now()) )
        return self.simulation.now() # to test .get_result()
    
    @schedule
    def method2(self, str_param): # with parameters
        self.traces.append( ("method2", self.simulation.now(), str_param) )
        return (self.simulation.now(), str_param) # to test .get_result()


class RequestManagerTestCase(unittest.TestCase): # classes under test: DelayedRequest, ScheduledRequest

    def setUp(self):
        self.simulation = Simulation()
        self.simulation.initialize()
        
        self.obj1 = FakeClass(self.simulation)
        self.obj2 = FakeClass(self.simulation)
        
    def test_get_result_method1(self):
        r = self.obj1.method1(at=100, simulation=self.simulation) # or directly: r = self.fc.method1(100)        
        self.simulation.simulate(1000)
        self.assertEquals(100, r.get_result())
        
    def test_get_result_method2(self):
        r = self.obj1.method2(at=200, simulation=self.simulation, str_param="helloworld")
        self.simulation.simulate(1000)
        self.assertEquals((200, "helloworld"), r.get_result())
        
    def test_scheduled_method1(self):
        self.obj1.method1(at=100)
        self.obj1.method1(at=300)
        self.obj2.method1(at=500)
        
        self.simulation.simulate(1000)
        
        self.assertItemsEqual( ( ("method1", 100), ("method1", 300) ), self.obj1.traces)
        self.assertItemsEqual( ( ("method1", 500),  ), self.obj2.traces)
    
    def test_scheduled_method2(self):
        self.obj1.method2(at=500, str_param="gato")
        self.obj1.method2(at=300, str_param="perro")
        self.obj2.method2(at=100, str_param="iguana")
        
        self.simulation.simulate(1000)
        
        self.assertItemsEqual( ( ("method2", 300, "perro"), ("method2", 500, "gato") ), self.obj1.traces)
        self.assertItemsEqual( ( ("method2", 100, "iguana"),  ), self.obj2.traces)
    
    def test_scheduled_methods_all(self):
        self.obj1.method2(at=600, str_param="lagartija")
        self.obj1.method1(at=400)
        self.obj1.method2(at=500, str_param="gato")
        
        self.obj2.method1(at=300)
        self.obj2.method2(at=100, str_param="iguana")
        self.obj2.method2(at=200, str_param="salamandra")
        
        self.simulation.simulate(1000)
        
        self.assertItemsEqual( ( ("method1", 400), ("method2", 500, "gato"), ("method2", 600, "lagartija") ), self.obj1.traces)
        self.assertItemsEqual( ( ("method1", 300), ("method2", 100, "iguana"), ("method2", 200, "salamandra")  ), self.obj2.traces)


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
