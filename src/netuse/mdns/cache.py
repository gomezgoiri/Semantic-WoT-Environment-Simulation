'''
Created on Jan 12, 2013

@author: tulvur
'''

from random import Random
from SimPy.Simulation import Process

class Cache(Process):
    
    WHEN_FIELD = 0
    ACTION_FIELD = 1 # what to do
    RECORD_FIELD = 2
    
    EVENT_USE_MULTICAST = "response_by_multicast"
    EVENT_NOT_KNOWN_ANSWER = "unadded_known_answer_suppression"
    EVENT_RENEW = "try_to_renew"
    
    def __init__(self, sim):
        super(Cache, self).__init__(sim=sim)
        self.pending_events = [] # tuples with the form (when, action, record)
        self.records = [] # cached records
        self._random = Random()
    
    def _delete_events_for_record(self, record):
        to_delete = []
        for event in self.pending_events:
            if event[Cache.RECORD_FIELD] == record:
                to_delete.append(event)
        
        for event in to_delete:
            self.pending_events.remove(event)
    
    def _get_time_after_percentage(self, ttl, percentage):
        """Percentage example: 0.45 (means 45%)"""
        return self.sim.now() + ttl * percentage
    
    def _create_new_events(self, record):
        ttl = record.ttl
        
        # at 1/4 of the TTL => no more QU responses
        when = self._get_time_after_percentage(ttl, 0.25)
        self.pending_events.append( (when, Cache.EVENT_USE_MULTICAST, record) )
        
        # at 1/2 of the TTL => does not add to known answer suppression
        when = self._get_time_after_percentage(ttl, 0.5)
        self.pending_events.append( (when, Cache.EVENT_NOT_KNOWN_ANSWER, record) )
        
        # section 5.2, http://tools.ietf.org/html/draft-cheshire-dnsext-multicastdns-15
        # at 80%, 85%, 90% and 95% of the TTL => try to renew the record
        for percentage in ( 80, 85, 90, 95 ):
            percentage_with_variation = (percentage + self._random.random()*2) / 100.0 # 2% of variation
            when = self._get_time_after_percentage(ttl, percentage_with_variation)
            self.pending_events.append( (when, Cache.EVENT_RENEW, record) )
    
    def cache_record(self, record):
        self._delete_events_for_record(record)
        self._create_new_events(record)
        
        self.records.remove(record) # does delete the previous one?
        self.records.append(record)
    
    def wait_for_next_event(self):
        pass