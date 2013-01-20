'''
Created on Jan 12, 2013

@author: tulvur
'''

from copy import deepcopy
from random import Random
from netuse.sim_utils import Timer
from netuse.mdns.packet import DNSPacket, Query, SubQuery
from SimPy.Simulation import Process, SimEvent, waitevent

class Responder(Process):
    
    ANSWER_AT_FIELD = 0
    QUERY_FIELD = 1
    
    def __init__(self, sim, sender=None):
        super(Responder, self).__init__(sim=sim)
        self._random = Random()
        self.__new_query_queued = SimEvent(name="new_query_queued", sim=sim)
        self.local_records = {} # key: record, value: last time advertised
        self.queued_queries = [] # tuple: ( when to answer, query )
        self.sender = sender
    
    def record_changes(self, record):
        for old_record in self.local_records.iterkeys():
            if record == old_record:
                return record.have_data_changed(old_record)
        return False # if that record didn't exist before
    
    def write_record(self, record):
        if record in self.local_records:
            if self.record_changes(record):
                # "Whenever a host has a resource record with new data"
                self.announce(record)
        else:
            # "Whenever a host has a resource record with new data"
            self.local_records[record] = -1
            self.announce(record)
    
    def something_happened(self):
        # Whenever it might potentially be new data (e.g. after rebooting, waking from
        # sleep, connecting to a new network link, changing IP address, etc.)
        for record in self.local_records.iterkeys():
            self.announce(record)
    
    # 10.2 Announcements to Flush Outdated Cache Entries
    def announce(self, announced_record):
        # TODO optimize to announce more than one? is that possible according to the standard?
        
        # Generating a fake query which will never be sent
        sq = SubQuery(announced_record.name, announced_record.type)
        # They may know my other records, I'm just announcing one
        known_answers = [record for record in self.local_records if record!=announced_record]
        q = Query( queries = [sq,], known_answers = known_answers )
        
        # a little trick here, we queue a false query which will result in a response
        # containing the record we want to announce
        self.queue_query(q)
    
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
            if not self.queued_queries: # if it's empty...
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
        answers = self._get_possible_answers(query)
        self._suppress_known_answers(query, answers)
        if len(answers)>0: # avoid sending empty UDP messages!
            self._send_using_proper_method(query, answers)
    
    def _get_possible_answers(self, query):
        answers = []
        for subquery in query.queries:
            for record in self.local_records.iterkeys():
                if subquery.record_type == "PTR": # special queries in DNS-SD!
                    
                    if subquery.name == "_services._dns-sd._udp.local":
                        answers.append( deepcopy(record) ) # all of the records
                    elif record.name.endswith(subquery.name):
                        answers.append( deepcopy(record) ) # all of the records
                
                elif subquery.name == record.name and subquery.record_type == record.type:
                    answers.append( deepcopy(record) )
        return answers
    
    def _suppress_known_answers(self, query, answers):
        # Section 7.1.  Known-Answer Suppression
        for known_answer in query.known_answers:
            for record in answers:
                if known_answer.name == record.name and known_answer.type == record.type:
                    answers.remove(record)
    
    def _send_using_proper_method(self, query, answers):
        unicast = query.question_type is "QU" # unicast type
        
        # See 5.4 Questions Requesting Unicast Responses
        if unicast:
            # event if it was marked as unicast, can be sent as multicast
            for record in answers:
                thresold_time = record.ttl * 1000 * 0.25 # ttl is measured in seconds and simulation time in ms!
                last_time_sent = self.local_records[record]
                now = self.sim.now()
                
                if last_time_sent==-1: # never sent before
                    unicast = False
                    self.local_records[record] = now
                elif ( now - last_time_sent ) > thresold_time:
                    unicast = False # not recently advertised, send using multicast
                    self.local_records[record] = now
        
        
        if unicast:
            self.sender.send_unicast( query.to_node, DNSPacket(ttype=DNSPacket.TYPE_RESPONSE, data=answers) )
        else:
            self.sender.send_multicast( DNSPacket(ttype=DNSPacket.TYPE_RESPONSE, data=answers) )