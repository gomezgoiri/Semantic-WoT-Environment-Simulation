'''
Created on Oct 29, 2012

@author: tulvur
'''

import os
import sys
import unittest

def create_test_suite_for_directory(base_file, recursive=True):    
    path_to_module = os.path.dirname(base_file)
    suite = unittest.TestSuite()
    add_to_test_suite_rec(suite, unittest.TestLoader(), path_to_module, recursive)
    return suite
                
def add_to_test_suite_rec(suite, loader, directory, recursive=True):
    sys.path.append(directory)
    files_in_dir = os.listdir(directory)
    
    for entry in files_in_dir:
        modname = os.path.splitext(entry)[0]
        if entry.endswith("py") and entry.startswith("test_"):
            entry = __import__( modname,{},{},['1'] )
            suite.addTest(loader.loadTestsFromModule(entry))
        elif os.path.isdir(entry):
            if recursive:
                try:
                    subdirectory = directory + "/" + entry
                    add_to_test_suite_rec(suite, loader, subdirectory, recursive)
                except:
                    pass # not valid entry