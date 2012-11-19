'''
Created on Sep 26, 2012

@author: tulvur
'''

from time import time
from abc import ABCMeta, abstractmethod


class AbstractTracer(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    @abstractmethod
    def trace(self, timestamp, client, server, path, status, response_time):
        pass

# http://stackoverflow.com/questions/3167494/how-often-does-python-flush-to-a-file
class Flusher(object):
    '''
        To force flush to a file depending on the number of writes or the time since the last flush.
        
        Using this class, we can check the simulation output in real-time.
    '''
    
    WRITES = 10 # write before flushing
    TIME = 1000 # time before last flush
    
    def __init__(self):
        self.countdown = Flusher.WRITES
        self.last_flush = 0
    
    def force_flush(self):
        t = time()
        if self.countdown<0 or (t-self.last_flush)<Flusher.TIME:
            self.countdown = Flusher.WRITES
            self.last_flush = t
            return True # you need to flush
        return False # don't need to force the flush

class FileTracer(AbstractTracer):
    
    def __init__(self, filename='/tmp/workfile'):
        self.filename = filename
        self.flusher = Flusher()
    
    def start(self):
        self.f = open(self.filename, 'w')
        
    def stop(self):
        self.f.close()
    
    def trace(self, timestamp, client, server, path, status, response_time):
        self.f.write("%0.2f\t%0.2f\t%s\t%s\t%s\t%d\n"%(timestamp,response_time,client,server,path,status))
        
        if self.flusher.force_flush():
            self.f.flush()


class MongoDBTracer(AbstractTracer):
    
    def __init__(self, execution):
        self.execution = execution
    
    def start(self):
        pass
        
    def stop(self):
        #self.execution.save()
        pass
        # Apparently, calling to self.execution.save() each time an element
        # is appended to the list introduces a huge latency
    
    # TODO store path!
    def trace(self, timestamp, client, server, path, status, response_time):
        from netuse.database.results import NetworkTrace
        n = NetworkTrace(
            execution=self.execution,
            timestamp=timestamp,
            client=client,
            server=server,
            path=path,
            status=status,
            response_time=response_time)
        n.save()