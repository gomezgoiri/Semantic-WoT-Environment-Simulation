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

import unittest
from netuse.triplespace.our_solution.consumer.time_update import UpdateTimesManager

class UpdateTimesManagerTestCase(unittest.TestCase):

    def test_add_updatetime(self):
        rc = UpdateTimesManager()
        
        l = []
        for i in range(1, 101, 10):
            rc.add_updatetime(i)
            l.append(i)
            self.assertEquals(rc.last_updates, l)
        
        rc.add_updatetime(14)
        self.assertEquals(rc.last_updates, [11, 21, 31, 41, 51, 61, 71, 81, 91, 14])
        
    
    def test_get_updatetime(self):
        rc = UpdateTimesManager()
        self.assertEquals(rc.get_updatetime(), UpdateTimesManager.DEFAULT_UPDATE_TIME)
        
        for i in range(0, UpdateTimesManager.MIN_UPDATE_RATE*10, UpdateTimesManager.MIN_UPDATE_RATE-10):
            rc.add_updatetime(i)
        self.assertEquals(rc.get_updatetime(), UpdateTimesManager.MIN_UPDATE_RATE)
        
        middle_rate = (UpdateTimesManager.MAX_UPDATE_RATE - UpdateTimesManager.MIN_UPDATE_RATE) / 2 + UpdateTimesManager.MIN_UPDATE_RATE
        for i in range(0, middle_rate*10, middle_rate):
            rc.add_updatetime(i)
        self.assertEquals(rc.get_updatetime(), middle_rate)
        
        for i in range(0, UpdateTimesManager.MAX_UPDATE_RATE*10, UpdateTimesManager.MAX_UPDATE_RATE+10):
            rc.add_updatetime(i)
        self.assertEquals(rc.get_updatetime(), UpdateTimesManager.MAX_UPDATE_RATE)
            

if __name__ == '__main__':
    unittest.main()