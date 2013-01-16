'''
Created on Jan 16, 2013

@author: tulvur
'''

import sys
import unittest
from testing.utils import create_test_suite_for_directory

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = create_test_suite_for_directory(sys.modules[__name__].__file__)
    results = runner.run(suite)