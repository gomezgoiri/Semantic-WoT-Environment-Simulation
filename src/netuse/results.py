'''
Created on Jan 2, 2012

@author: tulvur
'''
from SimPy.Simulation import random, Monitor

class ExecutionData(object):
    def __init__(self):
        self.requests = {"timeout": [],
                         "server-error": 0,
                         "success": [],
                         "failure": [],
                         "data-exchanged": 0}
        self.response_time_monitor = Monitor()

class G:  # global variables
    Rnd = random.Random(12345)
    timeout_after = 2000
    defaultSpace = "http://www.default.es/space"
    executionData = ExecutionData()
    
    @staticmethod
    def newExecution():
        G.executionData = ExecutionData()