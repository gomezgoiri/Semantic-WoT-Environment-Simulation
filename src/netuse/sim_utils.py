# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import inspect
from functools import wraps
from SimPy.Simulation import Process, SimEvent, hold

# def funcion(*args, **kwargs):
#    print args
#    print kwargs

# funcion(5,6,7)
# >> (5,6,7)
# >> {}

# funcion(5,6, a=9, b= 10)
# >> (5,6)
# >> { 'a' : 9, 'b' : 10 }

# funcion(a = 9, b = 10)
# >> ()
# >> { 'a' : 9, 'b' : 10 }


# Can be used to avoid common bugs using SimPy's activate function with a Process
def activatable(f):
    '''
    Checks that a method can be activated and activates it if so.
    
    If no "at" or "delay" arguments are provided, the method will behave as if nothing happened.
    This behavior can be useful, to simply annotate the method without breaking backwards compatibility with SimPy.
    
    This wrapper may be useful for:
        a) Avoid common bugs using SimPy's activate function with a Process.
        b) Visually check which functions/methods can/will be called by SimPy.
    '''
    @wraps(f)
    def wrapped(self, at = None, delay = None, *args, **kwargs):
        #if simulation is None:
        #    raise Exception("To activate a method a simulation object should be passed as argument.")
        if not inspect.isgeneratorfunction(f):
            raise Exception("SimPy needs this method to be a generator to activate it.")
        
        if at is None and delay is None:
            # somebody wants to activate it in the SimPy fashion by himself/herself, do nothing, just call the function
            # This can be useful, to simply annotate the method without breaking backwards compatibility of the method
            return f(self, *args, **kwargs)
        else:
            at = 'undefined' if at is None else at
            delay = 'undefined' if delay is None else delay
            
            # If everything is OK, activate it.
            self.sim.activate(self, f(self, *args, **kwargs), at=at, delay=delay)
    
    return wrapped


def schedule(f):
    '''
    Starts the decorated method at "at" during the simulation process.
    
    Note that each method of an object can only be activated once, so using this wrapper, we ensure
    that a new "SimPy Process" is created for each scheduled method.
    
    On the other hand, if no values are provided for "at", "delay" and "simulation",
    a normal call to the method will be performed.
    This may be desirable to call the method within the simulation or a test.
    '''
    @wraps(f)
    def wrapped(self, at = None, delay = None, simulation=None, *args, **kwargs):
        if simulation is None:
            # the default attribute my own classes may have to store simulation objects
            if hasattr(self, 'simulation'):
                simulation = self.simulation
            # the attribute SimPy's "Process" classes have to store simulation objects
            elif hasattr(self, 'sim'):
                simulation = self.sim
            elif at is None and delay is None:
                # somebody may want to just call the function.
                # E.g.: if he is testing it or if it already called within a simulation.
                return f(self, *args, **kwargs)
            else:
                raise Exception("The simulation object should be accessible either as an argument of the wrapper or as an attribute of the class being scheduled.") 
        
        if at is None and delay is None:
            # somebody may want to just call the function.
            # E.g.: if he is testing it or if it already called within a simulation.
            return f(self, *args, **kwargs)
        else:
            at = 'undefined' if at is None else at
            delay = 'undefined' if delay is None else delay
        
            sf = ScheduledFunction(self, f, args, kwargs, sim=simulation)
            sf.call(at=at, delay=delay)
            # Or if we don't want to use Activa
            # simulation.activate(sf, sf.do_after_waiting(), at=starts_at)
            
            #return f(self, *args, **kwargs)
            # If we care about the results, we should:
            #   - Receive a result listener as a parameter.
            #   - Return a wrapper which will contain the result.
            return sf.result
    
    return wrapped


class ScheduledFunction(Process):
    
    def __init__(self, objct, method, args, kwargs, sim=None):
        super(ScheduledFunction, self).__init__(sim=sim)
        self.result = ResultContainer()
        self.objct = objct
        self.method = (method, )
        self.args = args
        self.kwargs = kwargs
    
    @activatable
    def call(self):
        yield hold, self, 0 # needs to be a generator
        result = self.method[0](self.objct, *self.args, **self.kwargs)
        self.result.set_result( result )


class ResultContainer(object):
    def __init__(self):
        self.__result = None
        self.__has_result = False
    
    def set_result(self, result):
        self.__result = result
        self.__has_result = True
        
    def get_result(self):
        return self.__result
    
    def has_result(self):
        return self.__has_result

        
class Timer(Process):
    def __init__(self, waitUntil=10000.0, name="timer", sim=None):
        super(Timer, self).__init__(name=name, sim=sim)
        self.__timeout = waitUntil
        self.event = SimEvent(name="timer_event", sim=sim)
        self.ended = False
        
    def wait(self):
        yield hold, self, self.__timeout
        self.ended = True
        self.event.signal()