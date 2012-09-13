'''
Created on Jan 2, 2012

@author: tulvur
'''
import time
from SimPy.Simulation import random, Monitor
from netuse.database.results import NetworkTrace

class FileTracer:
    
    def __init__(self, filename='/tmp/workfile'):
        self.filename = filename
    
    def start(self):
        self.f = open(self.filename, 'w')
        
    def stop(self):
        self.f.close()
    
    def trace(self, timestamp, client, server, status, response_time):
        self.f.write("%0.2f\t%s\t%s\t%d\n"%(timestamp,client,server,status))
        
class MongoDBTracer:
    
    def __init__(self, execution):
        self.execution = execution
    
    def start(self):
        pass
        
    def stop(self):
        self.execution.save()
        # Apparently, calling to self.execution.save() each time an element
        # is appended to the list introduces a huge latency
    
    def trace(self, timestamp, client, server, status, response_time):
        n = NetworkTrace(
            timestamp=timestamp,
            client=client,
            server=server,
            status=status,
            response_time=response_time)
        self.execution.requests.append(n)
        n.save()
    

class G:  # global variables
    Rnd = random.Random(12345)
    timeout_after = 2000
    defaultSpace = "http://www.default.es/space"
    _tracer = None
    
    
    @staticmethod
    def setNewExecution(execution):
        # G._tracer = FileTracer('/tmp/workfile')
        G._tracer = MongoDBTracer(execution)
        G._tracer.start()
        
    @staticmethod
    def traceRequest(timestamp, client, server, status, response_time):
        #t1 = time.time()
        G._tracer.trace(timestamp, client, server, status, response_time)
        #print time.time()-t1
    
    @staticmethod
    def shutdown():
        G._tracer.stop()