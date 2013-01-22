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
    def trace_query(self, timestamp, fromm, query):
        pass
    
    @abstractmethod
    def trace_unicast_response(self, timestamp, fromm, answers, receiver):
        pass
    
    @abstractmethod
    def trace_multicast_response(self, timestamp, fromm, answers):
        pass


class FileUDPTracer(AbstractUDPTracer):
    
    def __init__(self, filename='/tmp/workfile', details=False):
        self.filename = filename
        self.details = details
        self.flusher = Flusher()
    
    def start(self):
        self.f = open(self.filename, 'w')
        
    def stop(self):
        self.f.close()
        
    def _trace_subqueries(self, queries):
        self.f.write( "\tSubqueries:\n" )
        for subquery in queries:
            self.f.write("\t\t%s\t%s\n"%(subquery.record_type,subquery.name))
        
    def _trace_known_answers(self, known_answers):
        self.f.write( "\tKnown answers:\n" )
        for known_answer in known_answers:
            self.f.write("\t\t%s\t%s\n"%(known_answer.type,known_answer.name))
    
    def _trace_answers(self, answers):
        self.f.write( "\tAnswers:\n" )
        for answer in answers:
            self.f.write( "\t\t%s\n"%(answer) )
    
    def trace_query(self, timestamp, fromm, query):
        self.f.write("%0.2f\t%s\t%s\n"%(timestamp, fromm, query.question_type))
        if self.details:
            self._trace_subqueries(query.queries)
            self._trace_known_answers(query.known_answers)
        
        if self.flusher.force_flush():
            self.f.flush()
    
    def _trace_response(self, timestamp, fromm, response_type, answers):
        self.f.write( "%0.2f\t%s\t%s\n" % (timestamp, fromm, response_type) )
        
        if self.details:
            self._trace_answers(answers)
        
        if self.flusher.force_flush():
            self.f.flush()
    
    def trace_unicast_response(self, timestamp, fromm, answers, receiver):
        self._trace_response( timestamp, fromm, "unicast (to %s)"%(receiver), answers )
            
    def trace_multicast_response(self, timestamp, fromm, answers):
        self._trace_response( timestamp, fromm, "multicast", answers )


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
    
    def _get_mongoengine_record(self, record):
        if record.type == "TXT":
            from netuse.database.results import TXTRecord
            return TXTRecord( name = record.name,
                              ttl = record.ttl,
                              keyvalues = record.keyvalues )
        elif record.type == "PTR":
            from netuse.database.results import PTRRecord
            return PTRRecord( name = record.name,
                              ttl = record.ttl,
                              domain_name = record.domain_name )
        elif record.type == "SVR":
            from netuse.database.results import SVRRecord
            return SVRRecord( name = record.name,
                              ttl = record.ttl,
                              hostname = record.hostname,
                              port = record.port )
        else:
            raise Exception("Not valid register")
    
    def _get_mongoengine_list_records(self, records):        
        result = []
        for record in records:
            me_rec = self._get_mongoengine_record(record)
            me_rec.save()
            result.append( me_rec )
        return result
    
    def _get_mongoengine_subqueries(self, queries):
        from netuse.database.results import MDNSSubQuery
        
        result = []
        for query in queries:
            subquery = MDNSSubQuery(name=query.name, record_type=query.record_type)
            subquery.save()
            result.append( subquery )
            
        return result
    
    def trace_query(self, timestamp, fromm, query):
        from netuse.database.results import MDNSQueryTrace
        queries = self._get_mongoengine_subqueries(query.queries)
        known_answers = self._get_mongoengine_list_records(query.known_answers)
        n = MDNSQueryTrace(
                execution = self.execution,
                timestamp = timestamp,
                fromm = fromm,
                question_type = query.question_type,
                queries = queries,
                known_answers = known_answers
            )
        n.save()
    
    def trace_unicast_response(self, timestamp, fromm, answers, receiver):
        from netuse.database.results import MDNSAnswerTrace
        me_answers = self._get_mongoengine_list_records(answers)
        n = MDNSAnswerTrace(
                execution = self.execution,
                timestamp = timestamp,
                fromm = fromm,
                answers = me_answers,
                to = receiver
            )
        n.save()
    
    def trace_multicast_response(self, timestamp, fromm, answers):
        from netuse.database.results import MDNSAnswerTrace
        me_answers = self._get_mongoengine_list_records(answers)
        n = MDNSAnswerTrace( # to == "all" by default
                execution = self.execution,
                timestamp = timestamp,
                fromm = fromm,
                answers = me_answers
            )
        n.save()