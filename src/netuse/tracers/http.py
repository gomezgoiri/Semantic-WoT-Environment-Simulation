'''
Created on Sep 26, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
from netuse.tracers.utils import Flusher


class AbstractHTTPTracer(object):
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


class FileHTTPTracer(AbstractHTTPTracer):
    
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


class MongoDBHTTPTracer(AbstractHTTPTracer):
    
    def __init__(self, execution):
        self.execution = execution
    
    def start(self):
        pass
        
    def stop(self):
        #self.execution.save()
        pass
        # Apparently, calling to self.execution.save() each time an element
        # is appended to the list introduces a huge latency
    
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