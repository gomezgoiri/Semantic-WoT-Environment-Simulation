'''
Created on Sep 26, 2012

@author: tulvur
'''

import unittest
from netuse.evaluation.utils import ParametrizationUtils
from netuse.evaluation.activity.processor import RawDataProcessor


class TestParametrizationUtils(unittest.TestCase):
    
    def setUp(self):
        self.path = "/home/tulvur/dev/dataset"
        self.samples = {
                        "aemet": "08001",
                        "bizkaisense": "7CAMPA",
                        "knoesis": "A02",
                        "morelab": "aitor-almeida"
                        }
        
    def assert_subfolder_as_expected(self, subfolder_name, min_number_elements):
        names = ParametrizationUtils.getStationNames(self.path, filter_subfolders=subfolder_name)
        self.assertTrue( min_number_elements <= len(names) )
        for subfolder, sample_element in self.samples.iteritems():
            if subfolder in subfolder_name:
                self.assertTrue( sample_element in names)
            else:
                self.assertFalse( sample_element in names)
    
    def test_getStationNames_all(self):
        names = ParametrizationUtils.getStationNames(self.path)
        self.assertTrue( 500 < len(names) )
        for subfolder, sample_element in self.samples.iteritems():
                self.assertTrue( sample_element in names)
        
    def test_getStationNames_subfolders(self):
        self.assert_subfolder_as_expected( ("aemet",), 245 )
        self.assert_subfolder_as_expected( ("bizkaisense",), 70 )
        self.assert_subfolder_as_expected( ("knoesis",), 400 )
        self.assert_subfolder_as_expected( ("morelab",), 28 )
        self.assert_subfolder_as_expected( ("morelab", "knoesis"), 228 )


if __name__ == '__main__':
    unittest.main()