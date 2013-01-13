'''
Created on Jan 12, 2013

@author: tulvur
'''

from copy import deepcopy
from random import Random
from netuse.sim_utils import Timer
from netuse.mdns.packet import DNSPacket
from SimPy.Simulation import Process, SimEvent, waitevent

class Responder(Process):
    
    ANSWER_AT_FIELD = 0
    QUERY_FIELD = 1
    
    def __init__(self, sim):
        super(Responder, self).__init__(sim=sim)
        self._random = Random()
        self.__new_query_queued = SimEvent(name="new_query_queued", sim=sim)
        self.local_records = {} # key: record, value: last time advertised
        self.queued_queries = [] # tuple: ( when to answer, query )
    
    def write_record(self, record):
        # if already existed, is overwritten
        self.local_records[record] = 0
    
    def queue_query(self, query):
        # TODO optimization:
        # if the query is already planned, don't answer twice in such a short period of time
        # if an answer for the same query was answered in the last 1000 ms, wait for the response
        
        if query.response_is_unique():
            # if the response is unique, answer within 10 ms
            when = self.sim.now() + self._random.random() * 10
            self.queued_queries.append( (when, query) )
        else:
            # delay between 20 and 120 ms
            when = self.sim.now() + 20 + self._random.random() * 100
            self.queued_queries.append( (when, query) )
        
        # sorts by the 1st element in the set
        self.queued_queries.sort(key=lambda tup: tup[0])
        
        # wake up wait_for_next_event method
        self.__new_query_queued.signal()
        
    def answer(self):
        while True:
            if not self.pending_events: # if it's empty...
                yield waitevent, self, (self.__new_query_queued,)
            else:
                next_query = self.queued_queries[0]
                
                if self.sim.now() < next_query[Responder.ANSWER_AT_FIELD]:
                    twait = next_query[Responder.ANSWER_AT_FIELD] - self.sim.now()
                    self.timer = Timer(waitUntil=twait, sim=self.sim)
                    self.timer.event.name = "sleep_until_next_query"
                    self.sim.activate(self.timer, self.timer.wait())
                    yield waitevent, self, (self.timer.event, self.__new_query_queued,)
                else:
                    del self.queued_queries[0] # query will be processed
                    self.process_query( next_query[Responder.QUERY_FIELD] )
    
    def process_query(self, query):
        answers = []
        
        for subquery in query.queries:
            for record in self.local_records.iterkeys():
                if subquery.name is record.name and subquery.record_type is record.type:
                    answers.append( deepcopy(record) )
        
        # Section 7.1.  Known-Answer Suppression
        for known_answer in query.known_answers:
            for record in answers:
                if known_answer.name is record.name and known_answer.record_type is record.type:
                    answers.append(record)
        
        unicast = query.question_type is "QU" # unicast type
        for record in answers:
            thresold_time = record.ttl * 0.4
            last_time_sent = self.local_records[record]
            now = self.sim.now()
            
            if (now - last_time_sent) > thresold_time:
                unicast = False # not recently advertised, send using multicast
            self.local_records[record] = self.sim.now()
        
        
        if unicast:
            self.send_unicast( DNSPacket(ttype="response", data=answers) )
        else:
            self.send_multicast( DNSPacket(ttype="response", data=answers) )