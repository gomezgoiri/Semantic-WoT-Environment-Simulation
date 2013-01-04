'''
Created on Jan 4, 2012

@author: tulvur
'''
import unittest
import datetime

from testing.utils import connect_to_testing_db
c = connect_to_testing_db()

from netuse.database.execution import Execution, ExecutionSet


class TestExecutions(unittest.TestCase):
    
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
        c.drop_database('tests')
    
    def test_get_simulated_execution_sets(self):
        for sim in ExecutionSet.objects.get_simulated():
            for ex in sim.executions:
                self.assertTrue(ex.execution_date is not None)
    
    def test_get_unsimulated_execution_sets(self):
        for unsim in ExecutionSet.objects.get_unsimulated():
            unexecuted = False
            for ex in unsim.executions:
                if ex.execution_date is None:
                    unexecuted = True
                    break
            self.assertTrue(unexecuted)


if __name__ == '__main__':
    unittest.main()