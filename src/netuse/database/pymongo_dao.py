'''
Created on Sep 27, 2012

@author: tulvur
'''

from pymongo import Connection

class PyMongoDAO(object):

    def __init__(self, database='network_usage'):
        self.connection = Connection('localhost', 27017)
        self.db = self.connection[database]
    
    def count_traces_in_execution(self, objectid):
        ex = self.db.executions.find_one({"_id": objectid}) # or directly find_one(objectid)        
        return len(ex['requests'])
    
    def get_simulated_execution_sets(self):
        esets = self.db.executionSet.find()
        simulated = []
        
        for es in esets:
            all_simulated = True
            for ex_dbref in es["executions"]:
                ex = self.db.executions.find_one(ex_dbref.id)
                if "execution_date" not in ex:
                    all_simulated = False
                    break
                           
            if all_simulated:
                simulated.append(es["_id"])
                
        return simulated
    
    
    def get_unsimulated_execution_sets(self):
        esets = self.db.executionSet.find()
        unsimulated = []
        
        for es in esets:
            for ex_dbref in es["executions"]:
                ex = self.db.executions.find_one(ex_dbref.id)
                if "execution_date" not in ex:
                    unsimulated.append(es["_id"])
                    break
                
        return unsimulated