'''
Created on Jan 12, 2013

@author: tulvur
'''

class Cache(object):
    
    WHEN_FIELD = 0
    ACTION_FIELD = 1 # what to do
    RECORD = 2
    
    def __init__(self):
        self.pending_events = [] # tuples with the form (when, action, record)
        self.records = [] # cached records
    
    def _delete_events_for_record(self, record):
        to_delete = []
        for event in self.pending_events:
            if event[Cache.RECORD] == record:
                to_delete.append(event)
        
        for event in to_delete:
            self.pending_events.remove(event)
    
    def _create_new_events(self, record):
        to_delete = []
        for event in self.pending_events:
            if event[Cache.RECORD] == record:
                to_delete.append(event)
        
        for event in to_delete:
            self.pending_events.remove(event)
    
    def cache_record(self, record):
        self._delete_events_for_record(record)
        self._create_new_events(record)
        
        self.records.remove(record) # does delete the previous one?
        self.records.append(record)
    
    def maintain(self):
        pass