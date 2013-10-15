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

import sys
import unittest
from testing.utils import create_test_suite_for_directory

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = create_test_suite_for_directory(sys.modules[__name__].__file__)
    results = runner.run(suite)