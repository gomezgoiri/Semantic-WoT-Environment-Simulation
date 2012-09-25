'''
Created on Jan 4, 2012

@author: tulvur
'''

import unittest
import datetime
from netuse.database.execution import Execution, ExecutionSet
from netuse.database.parametrization import Parametrization
from netuse.database.results import RequestsResults, Results

Execution.meta = {'collection': 'executionsTest'}
ExecutionSet.meta = {'collection': 'executionSetTest'}
        
class TestDatabase(unittest.TestCase):
    
    def reset_database(self):
        # or directly dropping the database
        for r in (Execution.objects, ExecutionSet.objects,):
            #print param.strategy
            r.delete()
    
    def create_simulated_execution(self):
        e = Execution(execution_date=datetime.datetime.now())
        e.save()
        return e
        
    def create_unsimulated_execution(self):
        e = Execution()
        e.save()
        return e
    
    def setUp(self):
        #self.reset_database()
        es_simulated = ExecutionSet(experiment_id="simulated01")
        es_simulated.addExecution(self.create_simulated_execution())
        es_simulated.addExecution(self.create_simulated_execution())
        es_simulated.save()
        
        es_unsimulated = ExecutionSet(experiment_id="unsimulated01")
        es_unsimulated.addExecution(self.create_unsimulated_execution())
        es_unsimulated.addExecution(self.create_unsimulated_execution())
        es_unsimulated.save()
        
        es_unsimulated = ExecutionSet(experiment_id="unsimulated01")
        es_unsimulated.addExecution(self.create_simulated_execution()) # the first has been executed
        es_unsimulated.addExecution(self.create_unsimulated_execution())
        es_unsimulated.save()
        
            
    def tearDown(self):
        self.reset_database()
    
    def test_get_simulated_execution_sets(self):
        for sim in ExecutionSet.get_simulated:
            for ex in sim.executions:
                self.assertTrue(ex.execution_date is not None)
    
    def test_get_unsimulated_execution_sets(self):
        for unsim in ExecutionSet.get_unsimulated:
            unexecuted = False
            for ex in unsim.executions:
                if ex.execution_date is None:
                    unexecuted = True
                    break
            self.assertTrue(unexecuted)

if __name__ == '__main__':
    unittest.main()