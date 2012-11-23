'''
Created on Nov 23, 2012

@author: tulvur
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