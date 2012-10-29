'''
Created on Jan 2, 2012

@author: tulvur
'''
from tempfile import mkdtemp
from SimPy.Simulation import random
from netuse.tracers import MongoDBTracer #FileTracer


class G:  # global variables
    Rnd = random.Random(12345)
    timeout_after = 2000
    defaultSpace = "http://www.default.es/space"
    dataset_path = "/home/tulvur/dev/dataset"
    temporary_path = None
    _tracer = None
    
    
    @staticmethod
    def setNewExecution(execution, tracer=None):
        temporary_path = mkdtemp(prefix="/tmp/exec_")
        
        # G._tracer = FileTracer('/tmp/workfile')
        G._tracer = MongoDBTracer(execution) if tracer==None else tracer
        G._tracer.start()
        
    @staticmethod
    def traceRequest(timestamp, client, server, path, status, response_time):
        #t1 = time.time()
        G._tracer.trace(timestamp, client, server, path, status, response_time)
        #print time.time()-t1
    
    @staticmethod
    def shutdown():
        G._tracer.stop()