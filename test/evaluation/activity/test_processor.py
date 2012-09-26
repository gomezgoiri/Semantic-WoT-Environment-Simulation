'''
Created on Sep 26, 2012

@author: tulvur
'''

import unittest
from netuse.evaluation.activity.processor import RawDataProcessor


class TestRawDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = RawDataProcessor()
        self.base_activity = []
        
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


if __name__ == '__main__':
    unittest.main()