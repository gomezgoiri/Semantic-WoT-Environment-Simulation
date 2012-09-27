'''
Created on Sep 27, 2012

@author: tulvur
'''

from pymongo import Connection
from mongoengine.connection import get_connection

class PyMongoDAO(object):

    def __init__(self, database='network_usage'):
        self.connection = get_connection() #Connection('localhost', 27017)
        self.db = self.connection[database]
    
    def count_traces_in_execution(self, objectid):
        #ex = self.db.executions.find_one({"_id": objectid}) # or directly find_one(objectid)
        
        # Pablo's original mongodb command:
        #db.eval(function(){return db.executions.find().map(function (obj) { return obj.requests.length });})
        server_func = """
                            function() {
                                return db.executions.find({'_id': ObjectId('%s')}).map(
                                    function (obj) {
                                        return obj.requests.length;
                                    }
                                );
                            }
                        """%(objectid)
                        
        #print server_func.replace("\n", "").replace("\t", "").replace("  ", "")
        return self.db.eval(server_func)
        # return len(ex['requests']) # easy way: it loads locally all the elements (AVOIDED!)
    
    def get_simulated_execution_sets(self):
        esets = self.db.executionSet.find()
        simulated = []
        
        for es in esets:
            all_simulated = True
            for ex_dbref in es["executions"]:
                ex = self.db.executions.find_one(ex_dbref.id, {'requests':0} )
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
                ex = self.db.executions.find_one(ex_dbref.id, {'requests':0})
                if "execution_date" not in ex:
                    unsimulated.append(es["_id"])
                    break
                
        return unsimulated
    
    def get_execution_ids(self, executionSet_id):
        es = self.db.executionSet.find_one({"_id": executionSet_id})                
        return [ex_dbref.id for ex_dbref in es["executions"]]