'''
Created on Jan 2, 2012

@author: tulvur
'''
import shutil
from tempfile import mkdtemp
from SimPy.Simulation import random
from netuse.tracers.http import MongoDBHTTPTracer #FileHTTPTracer
from netuse.tracers.udp import MongoDBUDPTracer


class G:  # global variables
    Rnd = random.Random(12345)
    timeout_after = 2000
    defaultSpace = "http://www.default.es/space"
    dataset_path = "/home/tulvur/dev/dataset"
    temporary_path = None
    _tracer = None
    _udp_tracer = None
    
    @staticmethod
    def setNewExecution(execution, tracer=None, udp_tracer=None):
        G.temporary_path = mkdtemp(prefix="/tmp/exec_")
        
        # G._tracer = FileHTTPTracer('/tmp/workfile')
        G._tracer = MongoDBHTTPTracer(execution) if tracer==None else tracer
        G._tracer.start()
        
        G._udp_tracer = MongoDBUDPTracer(execution) if udp_tracer==None else udp_tracer
        G._udp_tracer.start()
        
    @staticmethod
    def traceRequest(timestamp, client, server, path, status, response_time):
        #t1 = time.time()
        G._tracer.trace(timestamp, client, server, path, status, response_time)
        #print time.time()-t1
    
    @staticmethod
    def shutdown():
        G._tracer.stop()
        shutil.rmtree(G.temporary_path)