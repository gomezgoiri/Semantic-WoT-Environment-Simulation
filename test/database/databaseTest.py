'''
Created on Jan 4, 2012

@author: tulvur
'''

import unittest
from netuse.database.execution import Execution, ExecutionSet
from netuse.database.parametrization import Parametrization
from netuse.database.results import RequestsResults, Results

Execution.meta = {'collection': 'executionsTest'}
ExecutionSet.meta = {'collection': 'executionSetTest'}
        
class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        for r in (Execution.objects, ExecutionSet.objects,):
            #print param.strategy
            r.delete()
    
    def test_getGetStationNames(self):
        es = ExecutionSet()
        es.save()
        
        p = Parametrization()
        p.save()
        
        e = Execution(parameters=p)
        e.save()
        
        es.addExecution(e)
        es.save()
        
        es = ExecutionSet()
        es.save()
        
        e = Execution()
        e.save()
        
        es.addExecution(e)
        es.save()
        
        r = Results()
        r.save()
        
        e.results = r
        e.save()
        
        for r in ExecutionSet.get_unsimulated():
            print r.creation_date


if __name__ == '__main__':
    unittest.main()