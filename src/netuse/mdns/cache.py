'''
Created on Jan 12, 2013

@author: tulvur
'''

from random import Random
from netuse.sim_utils import Timer
from SimPy.Simulation import Process, SimEvent, waitevent

class Cache(Process):
    
    WHEN_FIELD = 0
    ACTION_FIELD = 1 # what to do
    RECORD_FIELD = 2
    
    EVENT_NOT_KNOWN_ANSWER = "unadded_known_answer_suppression"
    EVENT_RENEW = "try_to_renew"
    EVENT_FLUSH= "flush_record"
    
    def __init__(self, sim, record_observer=None):
        super(Cache, self).__init__(sim=sim)
        self.record_observer = record_observer
        self.__new_record_cached = SimEvent(name="new_record_cached", sim=sim)
        self._random = Random()
        self.pending_events = [] # tuples with the form (when, action, record)
        self.records = [] # cached records
    
    def _delete_events_for_record(self, record):
        to_delete = []
        for event in self.pending_events:
            if event[Cache.RECORD_FIELD] == record:
                to_delete.append(event)
        
        for event in to_delete:
            self.pending_events.remove(event)
    
    def _get_time_after_percentage(self, ttl, percentage):
        """Percentage example: 0.45 (means 45%)"""
        # remember that ttl is measured in seconds and simulation time in ms!
        return self.sim.now() + ttl * 1000 * percentage 
    
    def _create_new_events(self, record):
        ttl = record.ttl
        
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
        
        # sorts by the 1st element in the set
        self.pending_events.sort(key=lambda tup: tup[0])
        
        # wake up wait_for_next_event method
        self.__new_record_cached.signal()
    
    def flush_all(self):
        del self.records[:]
        del self.pending_events[:]
    
    # Inspired by RequestInstance class
    def wait_for_next_event(self):
        while True:
            
            if not self.pending_events: # if it's empty...
                yield waitevent, self, (self.__new_record_cached,)
            else:
                next_event = self.pending_events[0]
                
                if self.sim.now() < next_event[Cache.WHEN_FIELD]:
                    twait = next_event[Cache.WHEN_FIELD]-self.sim.now()
                    self.timer = Timer(waitUntil=twait, sim=self.sim)
                    self.timer.event.name = "sleep_until_next_event"
                    self.sim.activate(self.timer, self.timer.wait())
                    yield waitevent, self, (self.timer.event, self.__new_record_cached,)
                else:
                    del self.pending_events[0] # action will be taken
                    
                    if next_event[Cache.ACTION_FIELD] == Cache.EVENT_FLUSH:
                        # delete old record
                        self.records.remove( next_event[Cache.RECORD_FIELD] )
                        
                    elif next_event[Cache.ACTION_FIELD] == Cache.EVENT_RENEW:
                        if self.record_observer is not None:
                            self.record_observer.renew_record( next_event[Cache.RECORD_FIELD] )