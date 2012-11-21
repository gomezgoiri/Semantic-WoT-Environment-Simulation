'''
Created on Oct 29, 2012

@author: tulvur
'''

import sys
import unittest
from testing.utils import create_test_suite_for_directory

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    # TODO fix some tests in database until making this suite recursive
    suite = create_test_suite_for_directory(sys.modules[__name__].__file__, recursive=False)
    results = runner.run(suite)