'''
Created on Jan 4, 2012

@author: tulvur
'''
test_database = 'test'
from mongoengine import connect
connect(test_database, host="localhost") #, host="localhost" #, host='192.168.1.35', port=12345)


import unittest
import time
import random
import datetime
from pymongo import Connection

from netuse.database.pymongo_dao import PyMongoDAO
from netuse.database.results import NetworkTrace
from netuse.database.execution import Execution, ExecutionSet, AwesomerQuerySet
from netuse.database.parametrization import Parametrization

    
class TestDatabase(unittest.TestCase):
    
    node_names = ["n%d"%(n) for n in range(10)]
    status = [200, 404, 500]
    
    def createRandomNetworkTrace(self):
        t = NetworkTrace(timestamp = float(time.time()),
                        client = random.choice(TestDatabase.node_names),
                        server = random.choice(TestDatabase.node_names),
                        path = "fakepath",
                        status = random.choice(TestDatabase.status),
                        response_time = random.randint(5,25) )
        t.save()
        return t
    
    def createFakeExecution(self):
        e = Execution(execution_date = datetime.datetime.now())
        for _ in range(10):
            e.requests.append(self.createRandomNetworkTrace())
        e.save()
        return e
    
    def createSimulatedExecutionSet(self):
        es = ExecutionSet()
        for _ in range(10):
            es.executions.append(self.createFakeExecution())
        es.save()
        return es
    
    def createUnSimulatedExecutionSet(self):
        es = ExecutionSet()
        for _ in range(10):
            es.executions.append(self.createFakeExecution())
        
        unsimulated = Execution()
        unsimulated.save()
        es.executions.append(unsimulated)
        
        es.save()
        return es
    
    def setUp(self):
        self.simulated_ids = []
        
        self.simulated_ids.append( self.createSimulatedExecutionSet().id )
        self.createUnSimulatedExecutionSet()
        self.simulated_ids.append( self.createSimulatedExecutionSet().id )
        
        self.dao = PyMongoDAO(test_database)
        
    def tearDown(self):
        c = Connection()
        c.drop_database(test_database)
    
    def test_count_traces_in_execution(self):
        ex = Execution.objects.first() # take one
        self.assertEquals(10, self.dao.count_traces_in_execution(ex.id))
        
    def test_get_simulated_execution_sets(self):
        for sim_id in self.dao.get_simulated_execution_sets():
            self.assertTrue( sim_id in  self.simulated_ids )
            
    def test_get_unsimulated_execution_sets(self):
        for unsim_id in self.dao.get_unsimulated_execution_sets():
            self.assertTrue( unsim_id not in  self.simulated_ids )
        

if __name__ == '__main__':
    unittest.main()