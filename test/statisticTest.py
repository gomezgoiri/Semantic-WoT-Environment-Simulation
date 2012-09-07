'''
Created on Nov 30, 2011

@author: tulvur
'''
import unittest
from SimPy.Simulation import Monitor
from strateval.statistic import Stats
from mock import Mock

class TestStats(unittest.TestCase):
    
    def setUp(self):
        self.stats = Stats(None, None)
        mock = Mock()
        mock.return_value = True
        self.stats._Stats__is_significant = mock
        
        self.inactivity = Monitor()
        self.activity = Monitor()
    
    def assertInactivityContains(self, y, t):
        contains = False
        for event in self.inactivity:
            if event[0]==t and event[1]==y:
                contains = True
                break
        self.assertTrue(contains)
        
    
    #   |----|           (activity)
    #           |----|   (inactivity)
    def test_substractActivityFromInactivityNone1(self):
        self.activity.observe(4, t=4)
        self.inactivity.observe(4, t=10)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 1 )
        self.assertInactivityContains(4,10)
        
        
    #           |----|   (activity)
    #   |----|           (inactivity)
    def test_substractActivityFromInactivityNone2(self):        
        self.activity.observe(4, t=10)
        self.inactivity.observe(4, t=4)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 1 )
        self.assertInactivityContains(4,4)
        
        
    #   |------|      (activity)
    #       |------|  (inactivity)
    def test_substractActivityFromInactivity1(self):
        self.activity.observe(6, t=6)
        self.inactivity.observe(6, t=10)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 1 )
        self.assertInactivityContains(4,10)
    
    #   |----------|      (activity)
    #      |----|         (inactivity)
    def test_substractActivityFromInactivity2(self):
        self.activity.observe(10, t=10)
        self.inactivity.observe(4, t=6)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( 0, len(self.inactivity) )

    #       |---|      (activity)
    #   |----------|   (inactivity)
    def test_substractActivityFromInactivity3(self):
        self.activity.observe(4, t=6)
        self.inactivity.observe(10, t=10)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 2 )
        self.assertInactivityContains(2,2)
        self.assertInactivityContains(4,10)

    #       |----------|      (activity)
    #   |----------|          (inactivity)
    def test_substractActivityFromInactivity4(self):
        self.activity.observe(10, t=14)
        self.inactivity.observe(10, t=10)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 1 )
        self.assertInactivityContains(4,4)
        
    #   |----------------------|   (activity)
    #       |----|    |----|       (inactivity)
    def test_substractActivityFromInactivity5(self):
        self.activity.observe(4, t=16)
        self.activity.observe(4, t=8)
        self.inactivity.observe(20, t=20)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 3 )
        self.assertInactivityContains(4,4)
        self.assertInactivityContains(4,12)
        self.assertInactivityContains(4,20)
    
    #   |----------------------|   (activity)
    #       |----|    |----|       (inactivity)
    def test_substractActivityFromInactivity6(self):
        self.activity.observe(20, t=20)
        self.inactivity.observe(4, t=16)
        self.inactivity.observe(4, t=8)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 0 )
        
    #   |----------------------|       (activity)
    #       |----|        |-------|    (inactivity)
    def test_substractActivityFromInactivity7(self):
        self.activity.observe(20, t=20)
        self.inactivity.observe(4, t=16)
        self.inactivity.observe(4, t=22)
        
        self.stats.substractActivityFromInactivity(self.inactivity, self.activity)
        self.assertEquals( len(self.inactivity), 1 )
        self.assertInactivityContains(2,22)
        

if __name__ == '__main__':
    unittest.main()