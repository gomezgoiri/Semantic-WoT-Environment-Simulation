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
from netuse.evaluation.activity.processor import RawDataProcessor


class TestRawDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = RawDataProcessor()
        self.base_activity = []
        
        # N=[0-9]  =>  ( (N*10 + 1, N*10 + 4), ... )
        for init in range(1,101,10):
            self.base_activity.append((init, init+3))
    
    
    def test_select_overlaping_periods(self):
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (2,23))
        self.assertItemsEqual( overlaping, ((1, 4), (11, 14), (21, 24),) )
        
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (2,21))
        self.assertItemsEqual( overlaping, ((1, 4), (11, 14), (21, 24),) )
        
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (4,21))
        self.assertItemsEqual( overlaping, ((1, 4), (11, 14), (21, 24),) )
        
        # subsumed by the first one
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (2,3))
        self.assertItemsEqual( overlaping, ((1, 4),) )
        
        # upper limit equal
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (94,99))
        self.assertItemsEqual( overlaping, ((91, 94),) )
        
        # no overlaping
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (-3,0))
        self.assertFalse( overlaping )
        
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (5,7))
        self.assertFalse( overlaping )
        
        overlaping = self.processor._select_overlaping_periods(self.base_activity, (96,99))
        self.assertFalse( overlaping )
    
    
    def test_merge_periods_and_add(self):
        # WITH ONE OVERLAPING ACTIVITY
        
        #      |----|         (new_activity)
        #   |----------|      (older_activity)
        previous_activities = list(self.base_activity)
        overlaping = ( (21, 24), )
        new_activity = (22, 23)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( self.base_activity, previous_activities )
        
        #   |--------------|   (new_activity)
        #       |-----|        (older_activity)
        previous_activities = list(self.base_activity)
        overlaping = ( (1, 4), )
        new_activity = (0, 6)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((0, 6), (11, 14), (21, 24), (31, 34), (41, 44), (51, 54), (61, 64), (71, 74), (81, 84), (91, 94)), previous_activities )
        
        #        |----------| (new_activity)
        #   |----------|      (older_activity)
        previous_activities = list(self.base_activity)
        overlaping = ( (61, 64), )
        new_activity = (63, 68)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 4), (11, 14), (21, 24), (31, 34), (41, 44), (51, 54), (61, 68), (71, 74), (81, 84), (91, 94)), previous_activities )
        
        #   |----------|      (new_activity)
        #        |----------| (older_activity)
        previous_activities = list(self.base_activity)
        overlaping = ( (81, 84), )
        new_activity = (77, 81)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 4), (11, 14), (21, 24), (31, 34), (41, 44), (51, 54), (61, 64), (71, 74), (77, 84), (91, 94)), previous_activities )


        # WITH MORE THAN ONE OVERLAPING ACTIVITIES
        
        #   |------------------|   (new_activity)
        #     |--|  |--|  |--|     (older_activities)
        previous_activities = list(self.base_activity)
        overlaping = ( (1, 4), (11, 14), (21, 24), )
        new_activity = (2, 23)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 24), (31, 34), (41, 44), (51, 54), (61, 64), (71, 74), (81, 84), (91, 94)), previous_activities )
        
        #   |--------------|     (new_activity)
        #     |--|  |--|  |--|   (older_activities)
        previous_activities = list(self.base_activity)
        overlaping = ( (31, 34), (41, 44), (51, 54), )
        new_activity = (29, 52)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 4), (11, 14), (21, 24), (29, 54), (61, 64), (71, 74), (81, 84), (91, 94)), previous_activities )
        
        #      |--------------|  (new_activity)
        #    |--|  |--|  |--|    (older_activities)
        previous_activities = list(self.base_activity)
        overlaping = ( (31, 34), (41, 44), (51, 54), )
        new_activity = (32, 56)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 4), (11, 14), (21, 24), (31, 56), (61, 64), (71, 74), (81, 84), (91, 94)), previous_activities )

        #    |--------------|    (new_activity)
        #    |--|  |--|  |--|    (older_activities)
        previous_activities = list(self.base_activity)
        overlaping = ( (31, 34), (41, 44), (51, 54), )
        new_activity = (31, 54)
        self.processor._merge_periods_and_add(previous_activities, new_activity, overlaping)
        self.assertSequenceEqual( ((1, 4), (11, 14), (21, 24), (31, 54), (61, 64), (71, 74), (81, 84), (91, 94)), previous_activities )
    
    def test_calculate_total_activity_per_node(self):
        requests = []
        requests.append( FakeRequest('n1', 'n2', 10, 5) )
        requests.append( FakeRequest('n1', 'n2', 12, 5) )
        requests.append( FakeRequest('n1', 'n2', 20, 5) )
        requests.append( FakeRequest('n2', 'n3', 100, 5) )
        requests.append( FakeRequest('n2', 'n3', 110, 5) )
        requests.append( FakeRequest('n3', 'n4', 98, 5) )
        requests.append( FakeRequest('n4', 'n5', 95, 5) )
        requests.append( FakeRequest('n4', 'n5', 100, 5) )
        
        results = self.processor._calculate_total_activity_per_node( requests )
        self.assertEquals( results['n1'], (17-10) + (25-20)) # 10-17, 20-25
        self.assertEquals( results['n2'], (17-10) + (25-20) + (105-100) + (115-110) ) # 10-17, 20-25, 100-105, 110-115
        self.assertEquals( results['n3'], (105-98) + (115-110) ) # 98-105, 110-115
        self.assertEquals( results['n4'], 105-95) # 95-105
        self.assertEquals( results['n5'], 105-95) # 95-105


class FakeRequest(object):
    
    def __init__(self, client, server, timestamp, response_time):
        self.client = client
        self.server = server
        self.timestamp = timestamp
        self.response_time = response_time



if __name__ == '__main__':
    unittest.main()