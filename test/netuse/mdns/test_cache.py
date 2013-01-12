'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from mock import Mock, patch
from netuse.mdns.cache import Cache
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord

class TestCache(unittest.TestCase):
    
    def setUp(self):
        self.cache = Cache(None)
        for i in range(5):
            at = i * 10
            self.cache.pending_events.append((at, "blah", PTRRecord("name%d._http._tcp.local"%i)))
            self.cache.pending_events.append((at, "blah", SVRRecord("name%d._http._tcp.local"%i, None, None)))
            self.cache.pending_events.append((at, "blah", TXTRecord("name%d._http._tcp.local"%i, {})))
        self.assertEquals(15, len(self.cache.pending_events))
        
        self.sample_txt = TXTRecord("name0._http._tcp.local", {})
        self.sample_svr = SVRRecord("name2._http._tcp.local", None, None)
        self.sample_ptr = PTRRecord("name4._http._tcp.local")
    
    def does_contains_event(self, ttype, name, when=None, action=None):
        for event in self.cache.pending_events:
            cond = event is None or event[Cache.WHEN_FIELD]==when
            cond = cond and ( event is None or event[Cache.ACTION_FIELD]==action )
            cond = cond and event[Cache.RECORD_FIELD].name == name
            cond = cond and event[Cache.RECORD_FIELD].type == ttype
            if cond:
                return True
        return False
    
    def test_delete_events_for_record(self):
        self.cache._delete_events_for_record(self.sample_txt)
        self.assertEquals(14, len(self.cache.pending_events))
        self.assertFalse( self.does_contains_event(self.sample_txt.type, self.sample_txt.name) )
        
        self.cache._delete_events_for_record(self.sample_svr)
        self.assertEquals(13, len(self.cache.pending_events))
        self.assertFalse( self.does_contains_event(self.sample_svr.type, self.sample_svr.name) )
        
        self.cache._delete_events_for_record(self.sample_ptr)
        self.assertEquals(12, len(self.cache.pending_events))
        self.assertFalse( self.does_contains_event(self.sample_ptr.type, self.sample_ptr.name) )

    def test_create_new_events(self):
        self.cache._random = Mock()
        self.cache._random.random.side_effect = lambda *args: 0.5 # 0.5 * 2% == 1% of variation
        self.cache.sim = Mock()
        self.cache.sim.now.side_effect = lambda: 0
        
        self.sample_txt.ttl = 1000 # to ease calculations
        self.cache._create_new_events(self.sample_txt)
        self.assertEquals(15+6, len(self.cache.pending_events))
        
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=250, action=Cache.EVENT_USE_MULTICAST) )
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=500, action=Cache.EVENT_NOT_KNOWN_ANSWER) )
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=810, action=Cache.EVENT_RENEW) )
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=860, action=Cache.EVENT_RENEW) )
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=910, action=Cache.EVENT_RENEW) )
        self.assertTrue( self.does_contains_event(self.sample_txt.type, self.sample_txt.name, when=960, action=Cache.EVENT_RENEW) )
        


if __name__ == '__main__':    
    unittest.main()