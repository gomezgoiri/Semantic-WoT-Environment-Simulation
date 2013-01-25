'''
Created on Nov 28, 2011

@author: tulvur
'''

import copy
import unittest
from mock import Mock
from SimPy.Simulation import Simulation
from netuse.mdns.responder import Responder
from netuse.mdns.packet import Query, SubQuery
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord

class TestRecord(unittest.TestCase):
    
    def setUp(self):
        self.sample_ptr = PTRRecord("_http._tcp.local", "name0._http._tcp.local")
        self.sample_svr = SVRRecord("name0._http._tcp.local", None, None)
        self.sample_txt = TXTRecord("name0._http._tcp.local", {'v':1, 'g':23})
    
    def assert_fail_on_have_data_changed(self, record1, record2):
        try:
            record1.have_data_changed(record2)
            self.fail()
        except:
            pass # ok
    
    def test_have_data_changed_with_different_records(self):
        self.assert_fail_on_have_data_changed(self.sample_ptr, self.sample_svr)
        different_svr = SVRRecord("name1._http._tcp.local", None, None)
        self.assert_fail_on_have_data_changed(different_svr, self.sample_svr)
    
    def test_have_data_changed_ptr(self): # PTR never changes
        same_ptr_data = PTRRecord("_http._tcp.local", "name0._http._tcp.local")
        self.assertFalse( self.sample_ptr.have_data_changed(same_ptr_data) )
    
    def test_have_data_changed_svr(self):
        different_svr_data = SVRRecord("name0._http._tcp.local", "hostname1", 9900)
        self.assertTrue( self.sample_svr.have_data_changed(different_svr_data) )
        same_svr_data = SVRRecord("name0._http._tcp.local", None, None)
        self.assertFalse( self.sample_svr.have_data_changed(same_svr_data) )
    
    def test_have_data_changed_svr(self):
        different_txt_data = TXTRecord("name0._http._tcp.local", {'v':1, 'g':23, 'd':34})
        self.assertTrue( self.sample_txt.have_data_changed(different_txt_data) )
        same_txt_data = TXTRecord("name0._http._tcp.local", {'v':1, 'g':23})
        self.assertFalse( self.sample_txt.have_data_changed(same_txt_data) )


if __name__ == '__main__':    
    unittest.main()