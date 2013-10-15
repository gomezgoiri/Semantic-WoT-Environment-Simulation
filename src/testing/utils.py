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

import os
import sys
import time
import unittest
from netuse.tracers.udp import AbstractUDPTracer
from netuse.tracers.http import AbstractHTTPTracer


def connect_to_testing_db():
    from mongoengine import connect
    return connect('tests', host="localhost") #, host="localhost", port=12345)

def create_test_suite_for_directory(base_file, recursive=True):    
    path_to_module = os.path.dirname(base_file)
    suite = unittest.TestSuite()
    add_to_test_suite_rec(suite, unittest.TestLoader(), path_to_module, recursive)
    return suite
                
def add_to_test_suite_rec(suite, loader, directory, recursive=True):
    sys.path.append(directory)
    
    for entry in os.listdir(directory):
        entry_with_path = directory + "/" + entry
        modname = os.path.splitext(entry)[0]
        if entry.endswith("py") and entry.startswith("test_"):
            entry = __import__( modname,{},{},['1'] )
            suite.addTest(loader.loadTestsFromModule(entry))
        elif os.path.isdir(entry_with_path):
            if recursive:
                try:
                    add_to_test_suite_rec(suite, loader, entry_with_path, recursive)
                except:
                    pass # not valid entry

    sys.path.remove(directory)


class TimeRecorder(object):
    
    def __init__(self, msg = None):
        self.message = msg
        self.reset()
    
    def reset(self):
        self.time_passed = 0
    
    def start(self):
        self.t1 = time.time()
            
    def stop(self):
        self.time_passed += (time.time() - self.t1)
    
    def __str__(self):
        return "%0.3f %s"%(self.time_passed, "" if self.message is None else self.message)
    
    def __repr__(self):
        return self.__str__()


class TestingTracer(AbstractHTTPTracer, AbstractUDPTracer):
    
    def __init__(self):
        super(TestingTracer, self).__init__()
        self.traces = []
    
    def start(self):
        pass
        
    def stop(self):
        pass
    
    #def trace(self, **kwargs):
    #    self.traces.append( kwargs )
    
    def trace(self, timestamp, client, server, path, status, response_time):
        trace = {}
        trace['timestamp'] = timestamp
        trace['client'] = client
        trace['server'] = server
        trace['path'] = path
        trace['status'] = status
        trace['response_time'] = response_time
        self.traces.append( trace )
        
    def trace_query(self, timestamp, fromm, query):
        trace = {}
        trace['timestamp'] = timestamp
        trace['from'] = fromm
        trace['query'] = query
        self.traces.append( trace )
    
    def trace_unicast_response(self, timestamp, fromm, answers, receiver):
        trace = {}
        trace['timestamp'] = timestamp
        trace['from'] = fromm
        trace['answers'] = answers
        trace['receiver'] = receiver
        self.traces.append( trace )
    
    def trace_multicast_response(self, timestamp, fromm, answers):
        trace = {}
        trace['timestamp'] = timestamp
        trace['from'] = fromm
        trace['answers'] = answers
        trace['receiver'] = "all"
        self.traces.append( trace )