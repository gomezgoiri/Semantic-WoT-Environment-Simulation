'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from netuse.mdns.cache import Cache
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord

class TestCache(unittest.TestCase):
    
    def setUp(self):
        self.cache = Cache()
        for i in range(5):
            at = i * 10
            self.cache.pending_events.append((at, "blah", PTRRecord("name%d._http._tcp.local"%i)))
            self.cache.pending_events.append((at, "blah", SVRRecord("name%d._http._tcp.local"%i, None, None)))
            self.cache.pending_events.append((at, "blah", TXTRecord("name%d._http._tcp.local"%i, {})))
        self.assertEquals(15, len(self.cache.pending_events))
    
    def assert_not_event(self, ttype, name):
        for event in self.cache.pending_events:
            self.assertFalse( event[Cache.RECORD].name == name and event[Cache.RECORD].type == ttype)
    
    def test_delete_events_for_record(self):
        record_to_delete = TXTRecord("name0._http._tcp.local", {})
        self.cache._delete_events_for_record(record_to_delete)
        self.assertEquals(14, len(self.cache.pending_events))
        self.assert_not_event(record_to_delete.type, record_to_delete.name)
        
        record_to_delete = SVRRecord("name2._http._tcp.local", None, None)
        self.cache._delete_events_for_record(record_to_delete)
        self.assertEquals(13, len(self.cache.pending_events))
        self.assert_not_event(record_to_delete.type, record_to_delete.name)
        
        record_to_delete = PTRRecord("name4._http._tcp.local")
        self.cache._delete_events_for_record(record_to_delete)
        self.assertEquals(12, len(self.cache.pending_events))
        self.assert_not_event(record_to_delete.type, record_to_delete.name)

if __name__ == '__main__':    
    unittest.main()