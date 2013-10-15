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
from clueseval.clues.versions.management import VersionFactory, Version

class VersionFactoryTest(unittest.TestCase):

    def test_creation(self):
        vf = VersionFactory()
        
        version0 = vf.create_version()
        self.assertEquals(0, version0.version)
        
        version1 = vf.create_version()
        self.assertEquals(1, version1.version)
        self.assertEquals(version0.generation, version1.generation)


class VersionTest(unittest.TestCase):

    def test_less_than(self):
        version0 = Version(0, 0)
        version1 = Version(0, 1)
        self.assertTrue( version0 < version1 )
        
        version0 = Version(0, 1)
        version1 = Version(1, 0)
        self.assertTrue( version0 < version1 )
        
        version0 = Version(1, 1)
        version1 = Version(1, 0)
        self.assertFalse( version0 < version1 )
        
        version0 = Version(1, 0)
        version1 = Version(0, 1)
        self.assertFalse( version0 < version1 )
    
    def test_greater_than(self):
        version0 = Version(0, 0)
        version1 = Version(0, 1)
        self.assertTrue( version1 > version0 )
        
        version0 = Version(0, 1)
        version1 = Version(1, 0)
        self.assertTrue( version1 > version0 )
        
        version0 = Version(1, 1)
        version1 = Version(1, 0)
        self.assertFalse( version1 > version0 )
        
        version0 = Version(1, 0)
        version1 = Version(0, 1)
        self.assertFalse( version1 > version0 )
        
        
    def test_equals(self):
        version0 = Version(0, 0)
        version1 = Version(0, 0)
        self.assertTrue( version0 == version1 )
        
        version0 = Version(0, 0)
        version1 = Version(1, 0)
        self.assertFalse( version0 == version1 )
        
        version0 = Version(0, 0)
        version1 = Version(0, 1)
        self.assertFalse( version1 == version0 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreation']
    unittest.main()