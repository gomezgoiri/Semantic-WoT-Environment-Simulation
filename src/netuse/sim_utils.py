'''
Created on Sep 18, 2011

@author: tulvur
'''
from functools import wraps
from SimPy.Simulation import Process, activate, hold, now

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


def schedule(f):
    '''
    Starts the decorated method at "starts_at" during the simulation process.
    '''
    @wraps(f)
    def wrapped(self, starts_at, *args, **kwargs):
        # waits until starts_at and changes then calls the method
        sf = ScheduledFunction(self, f, args, kwargs)
        activate(sf, sf.do_after_waiting(), at=starts_at)
        
        #return f(self, *args, **kwargs)
        # If we care about the results, we should:
        #   - Receive a result listener as a parameter.
        #   - Return a wrapper which will contain the result.
        return sf.result
    
    return wrapped


class ScheduledFunction(Process):
    
    def __init__(self, objct, method, args, kwargs):
        super(ScheduledFunction, self).__init__()
        self.result = ResultContainer()
        self.objct = objct
        self.method = (method, )
        self.args = args
        self.kwargs = kwargs
        
    def do_after_waiting(self):
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