# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
''' 

from abc import ABCMeta#, abstractmethod

class Record(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, ttype, ttl):
        self.name = name # instance name or service name (e.g. query PTR)
        self.type = ttype
        self.ttl = ttl # remember that ttl is measured in seconds and simulation time in ms!
    
    def __eq__(self, record):
        return isinstance(record, Record) and self.type == record.type and self.name == record.name
    
    def __ne__(self, other):
        return not self == other
    
    # if I don't redefine this also, it won't work in some data structures (e.g. dictionaries)
    def __hash__(self):
        return  self.type.__hash__() + self.name.__hash__()
    
    def __str__(self):
        return "\t\t%s\t%s\tttl:%0.2f\n" % (self.type, self.name, self.ttl)
    
    def have_data_changed(self, old_record):
        if self != old_record:
            raise Exception("You are trying to compare data from different records.")
        return False


class PTRRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, domain_name):
        super(PTRRecord, self).__init__(name, "PTR", 75*60) # TTL: 75 mins
        # to browse all services, the name should be _services._dns-sd._udp.local
        self.domain_name = domain_name
    
    def __eq__(self, record):
        return super(PTRRecord, self).__eq__(record) and self.domain_name == record.domain_name
    
    # if I don't redefine this also, it won't work in some data structures (e.g. dictionaries)
    def __hash__(self):
        return super(PTRRecord, self).__hash__() + self.domain_name.__hash__()
    
    def __str__(self):
        return super(PTRRecord, self).__str__() + "\t%s" % (self.domain_name)
    
    # def have_data_changed(self, old_record)
    # If 2 PTR record are equal, they cannot change according to the fields they have

class TXTRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, keyvalues):
        super(TXTRecord, self).__init__(name, "TXT", 75*60) # TTL: 75 mins
        self.keyvalues = keyvalues # must be a dictionary
        # In reality, SVR record points to PTR record which has the name
    
    def __str__(self):
        return super(TXTRecord, self).__str__() + "\t%s" % (self.keyvalues)
    
    def have_data_changed(self, old_record):
        return super(TXTRecord, self).have_data_changed(old_record) or self.keyvalues != old_record.keyvalues

class SVRRecord(Record):
    __metaclass__ = ABCMeta
    
    def __init__(self, name, hostname, port):
        super(SVRRecord, self).__init__(name, "SVR", 120) # TTL: 120 seconds
        self.hostname = hostname # must be a dictionary
        self.port = port
        # The name issue was simplified.
        # In reality, SVR record points to PTR record which has the name
    
    # I'm not doing sth special with it, so I will not ovewrite the method
    # def __str__(self):
    
    def have_data_changed(self, old_record):
        return super(SVRRecord, self).have_data_changed(old_record) \
                or self.hostname != old_record.hostname \
                or self.port != old_record.port