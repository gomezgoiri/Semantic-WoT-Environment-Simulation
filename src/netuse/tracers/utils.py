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

from time import time

# http://stackoverflow.com/questions/3167494/how-often-does-python-flush-to-a-file
class Flusher(object):
    '''
        To force flush to a file depending on the number of writes or the time since the last flush.
        
        Using this class, we can check the simulation output in real-time.
    '''
    
    WRITES = 10 # write before flushing
    TIME = 1000 # time before last flush
    
    def __init__(self):
        self.countdown = Flusher.WRITES
        self.last_flush = 0
    
    def force_flush(self):
        t = time()
        if self.countdown<0 or (t-self.last_flush)<Flusher.TIME:
            self.countdown = Flusher.WRITES
            self.last_flush = t
            return True # you need to flush
        return False # don't need to force the flush