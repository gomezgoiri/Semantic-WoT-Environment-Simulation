'''
Created on Sep 22, 2012

@author: tulvur
'''

import json
from netuse.database.pymongo_dao import PyMongoDAO
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization
from netuse.evaluation.number_requests.strategies.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
    
    def _load(self, dao, executionSet_id, name, strategy, additionalFilter=None):
        nodes_and_requests = [] # tuples of 2 elements: number of nodes in the simulation and requests
        for execution_id in dao.get_execution_ids(executionSet_id):
            execution = Execution.objects(id=execution_id).exclude("requests").first()
            if execution.parameters.strategy==strategy:
                if additionalFilter==None or additionalFilter(execution.parameters):
                    num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                    num_requests = dao.count_traces_in_execution(execution_id) # len(execution.requests) # inefficient
                    nodes_and_requests.append((num_nodes, num_requests))
        
        # sort by num_nodes
        sort = sorted(nodes_and_requests)
        
        self.data[name] = {}
        self.data[name][DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        self.data[name][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
    
    def load_all(self):
        dao = PyMongoDAO()
        for executionSet_id in dao.get_simulated_execution_sets():
            self._load(dao, executionSet_id, DiagramGenerator.NB, Parametrization.negative_broadcasting)
            self._load(dao, executionSet_id, DiagramGenerator.OURS_1C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==1)
            self._load(dao, executionSet_id, DiagramGenerator.OURS_10C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==10)
            self._load(dao, executionSet_id, DiagramGenerator.OURS_100C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==100)

    def toJson(self):
        return json.dumps(self.data)


# Entry point for setup.py
def main():
    rdp = RawDataProcessor()
    rdp.load_all()
    json_txt = rdp.toJson()
    #print json_txt
    d = DiagramGenerator("Net usage", eval(json_txt))
    d.save('/tmp/example.pdf')


if __name__ == '__main__':
    main()