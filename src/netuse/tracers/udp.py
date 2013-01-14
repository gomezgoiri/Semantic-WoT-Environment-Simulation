'''
Created on Sep 26, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
from netuse.tracers.utils import Flusher


class AbstractUDPTracer(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    @abstractmethod
    def trace_query(self, timestamp, query):
        pass
    
    @abstractmethod
    def trace_unicast_response(self, timestamp, answers):
        pass
    
    @abstractmethod
    def trace_multicast_response(self, timestamp, answers):
        pass


class FileUDPTracer(AbstractUDPTracer):
    
    def __init__(self, filename='/tmp/workfile'):
        self.filename = filename
        self.flusher = Flusher()
    
    def start(self):
        self.f = open(self.filename, 'w')
        
    def stop(self):
        self.f.close()
        
    def _trace_subqueries(self, queries):
        self.f.write("\tSubqueries:\n")
        for subquery in queries:
            self.f.write("\t\t%s\t%s\n"%(subquery.record_type,subquery.name))
        
    def _trace_known_answers(self, known_answers):
        self.f.write("\tKnown answers:\n")
        for known_answer in known_answers:
            self.f.write("\t\t%s\t%s\n"%(known_answer.type,known_answer.name))
    
    def trace_query(self, timestamp, query):
        self.f.write("%0.2f\t%s\n"%(timestamp,query.question_type))
        self._trace_subqueries(query.queries)
        self._trace_known_answer(query.known_answers)
        
        if self.flusher.force_flush():
            self.f.flush()
    
    def _trace_response(self, timestamp, response_type, answers):
        self.f.write( "%0.2f\t%s\n" % (timestamp, response_type) )
        self.f.write( "\tAnswers:\n" )
        for answer in answers:
            self.f.write( "\t\t%s\n"%(answer) )
        
        if self.flusher.force_flush():
            self.f.flush()
    
    def trace_unicast_response(self, timestamp, answers):
        self._trace_response( timestamp, "unicast", answers )
            
    def trace_multicast_response(self, timestamp, answers):
        self._trace_response( timestamp, "multicast", answers )


class MongoDBUDPTracer(AbstractUDPTracer):
    
    def __init__(self, execution):
        self.execution = execution
    
    def start(self):
        pass
        
    def stop(self):
        #self.execution.save()
        pass
        # Apparently, calling to self.execution.save() each time an element
        # is appended to the list introduces a huge latency
    
    def trace_query(self, timestamp, query):
        pass
    
    @abstractmethod
    def trace_unicast_response(self, timestamp, answers):
        pass
    
    @abstractmethod
    def trace_multicast_response(self, timestamp, answers):
        pass
    
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
