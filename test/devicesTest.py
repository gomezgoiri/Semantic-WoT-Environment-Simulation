'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from mock import Mock, patch
from netuse.devices import XBee

def side_effect(*args):
    return args[0] + args[1]/2 # just to check how to configure different returns

rndMock = Mock()
rndMock.normalvariate.side_effect = side_effect
#rndMock.normalvariate.return_value = 0

class TestDeviceType(unittest.TestCase):
    
    #def setUp(self):

    def getMockedDevice(self, device):
        resources = Mock()
        resources.capacity = 10
        resources.n = 0
        device._DeviceType__resources = resources
        return device
    
    @patch('netuse.results.G.Rnd', rndMock) # new global unrandomized variable 
    def test_getTimeNeededToAnswer(self):        
        dev = self.getMockedDevice(XBee())
        
        #self.assertEquals(779.0, dev.getTimeNeededToAnswer())
        self.assertTimeNeeded(dev,1,0,(77,1)) # 1 resources being used (me!)
        self.assertTimeNeeded(dev,5,0,(392,8)) # 5 resources being used
        self.assertTimeNeeded(dev,7,2,(392,8)) # 5 resources being used
        self.assertTimeNeeded(dev,10,0,(775.0,8.0)) # 10 resources being used
        self.assertTimeNeeded(dev,20,10,(775.0,8.0)) # 10 resources being used
        
        
        self.assertTimeNeeded(dev,2,0,(155.75,2.75)) # =(392-77)/4*1 +77
        self.assertTimeNeeded(dev,3,0,(234.5,4.5)) # =(392-77)/4*2 +77
        self.assertTimeNeeded(dev,4,0,(313.25,6.25)) # =(392-77)/4*3 +77
        
        self.assertTimeNeeded(dev,6,0,(468.6,8.0)) # =(775-392)/4*1 +392
        self.assertTimeNeeded(dev,7,0,(545.2,8.0))
        self.assertTimeNeeded(dev,8,0,(621.8,8.0))
        self.assertTimeNeeded(dev,9,0,(698.4,8.0))
        
    def assertTimeNeeded(self, device, capacity, free_resources, expectParameters):
        device._DeviceType__resources.capacity = capacity
        device._DeviceType__resources.n = free_resources
        device.getTimeNeededToAnswer()
        rndMock.normalvariate.assert_called_with(expectParameters[0], expectParameters[1]) # for 10 concurrent requests

if __name__ == '__main__':    
    unittest.main()