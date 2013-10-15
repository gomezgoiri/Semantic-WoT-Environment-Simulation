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

from random import Random
from netuse.sim_utils import Timer
from SimPy.Simulation import Process, SimEvent, waitevent

# 7.3 Duplicate Question Suppression

class ContinuousQuerier(Process):
    """Check Section 5.2"""
    
    # the interval between the first two queries MUST be at least one second
    MINIMUM_FIRST_WAIT = 1000
    MINIMUM_INCREMENT_RATE = 2
    
    FIRST_WAIT = MINIMUM_FIRST_WAIT + 4000
    INCREMENT_RATE = MINIMUM_INCREMENT_RATE * 2
    
    def __init__(self, subquery, sim, sender=None):
        super(ContinuousQuerier, self).__init__(sim=sim)
        self.sender = sender
        # if there is a unique response, it should stop querying
        # I will assume that there is not unique response (asking for PTR records)
        self.subquery = subquery
        self._random = Random()
        self.stopped = False
        self.__stop = SimEvent(name="stop_continuous_querier", sim=sim)
    
    def query_continuously(self):
        # SHOULD also delay the first query of the series
        # by a randomly-chosen amount in the range 20-120ms.
        
        twait = 20 + self._random.random()*100
        timer = Timer(waitUntil=twait, sim=self.sim)
        self.sim.activate(timer, timer.wait())
        yield waitevent, self, (timer.event, self.__stop,)
        self.sender.send_query(self.subquery, to_node=self.sender.node_id) # joining a network
        
        # the interval between the first two queries MUST be at least one second
        twait = ContinuousQuerier.FIRST_WAIT
        while not self.stopped:
            timer = Timer(waitUntil=twait, sim=self.sim)
            self.sim.activate(timer, timer.wait())
            yield waitevent, self, (timer.event, self.__stop,)
            self.sender.send_query(self.subquery) # subsequent queries
            
            if twait!=3600000:
                # the intervals between successive queries MUST increase by at least a factor of two
                twait = twait * ContinuousQuerier.INCREMENT_RATE
                # When the interval between queries reaches or exceeds 60 minutes
                # a querier MAY cap the interval to a maximum of 60 minutes
                # and perform subsequent queries at a steady-state rate of one query per hour
                if twait>3600000:
                    twait = 3600000 # 1h
    
    def stop(self):
        self.stopped = True
        self.__stop.signal()
    
    def reset(self):
        self.stopped = False