'''
Created on Oct 29, 2012

@author: tulvur
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
    files_in_dir = os.listdir(directory)
    
    for entry in files_in_dir:
        modname = os.path.splitext(entry)[0]
        if entry.endswith("py") and entry.startswith("test_"):
            entry = __import__( modname,{},{},['1'] )
            suite.addTest(loader.loadTestsFromModule(entry))
        elif os.path.isdir(entry):
            if recursive:
                try:
                    subdirectory = directory + "/" + entry
                    add_to_test_suite_rec(suite, loader, subdirectory, recursive)
                except:
                    pass # not valid entry


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
        
    def trace_query(self, timestamp, query):
        trace = {}
        trace['timestamp'] = timestamp
        trace['query'] = query
        self.traces.append( trace )
    
    def trace_unicast_response(self, timestamp, answers, receiver):
        trace = {}
        trace['timestamp'] = timestamp
        trace['answers'] = answers
        trace['receiver'] = receiver
        self.traces.append( trace )
    
    def trace_multicast_response(self, timestamp, answers):
        trace = {}
        trace['timestamp'] = timestamp
        trace['answers'] = answers
        trace['receiver'] = "all"
        self.traces.append( trace )