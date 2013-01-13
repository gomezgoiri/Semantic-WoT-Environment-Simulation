'''
Created on Jan 12, 2013

@author: tulvur
'''
from abc import ABCMeta#, abstractmethod

class Record(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, ttype, ttl):
        self.name = name # instance name or service name
        self.type = ttype
        self.ttl = ttl
    
    def __eq__(self, record):
        return self.type == record.type and self.name == record.name

class PTRRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name):
        super(PTRRecord, self).__init__(name, "PTR", 75*60) # TTL: 75 mins
        # to browse, the name should be _services._dns-sd._udp.local

class TXTRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, keyvalues):
        super(TXTRecord, self).__init__(name, "TXT", 75*60) # TTL: 75 mins
        self.keyvalues = keyvalues # must be a dictionary
        # In reality, SVR record points to PTR record which has the name

class SVRRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, hostname, port):
        super(SVRRecord, self).__init__(name, "SVR", 120) # TTL: 120 seconds
        self.hostname = hostname # must be a dictionary
        self.port = port
        # The name issue was simplified.
        # In reality, SVR record points to PTR record which has the name