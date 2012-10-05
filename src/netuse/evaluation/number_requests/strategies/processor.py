'''
Created on Sep 22, 2012

@author: tulvur
'''

import json
from netuse.database.execution import ExecutionSet
from netuse.database.results import NetworkTrace
from netuse.database.parametrization import Parametrization
from netuse.evaluation.number_requests.strategies.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
        
    def _load(self, executionSet, name, strategy, additionalFilter=None):
        nodes_and_requests = [] # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if execution.parameters.strategy==strategy:
                if additionalFilter==None or additionalFilter(execution.parameters):
                    num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                    num_requests = NetworkTrace.objects(execution=execution.id).count()
                    nodes_and_requests.append((num_nodes, num_requests))
        
        # sort by num_nodes
        sort = sorted(nodes_and_requests)
        
        self.data[name] = {}
        self.data[name][DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        self.data[name][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
    
    def load_all(self):
        for executionSet in ExecutionSet.objects(experiment_id='network_usage').get_simulated():
            self._load(executionSet, DiagramGenerator.NB, Parametrization.negative_broadcasting)
            self._load(executionSet, DiagramGenerator.OURS_1C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==1)
            self._load(executionSet, DiagramGenerator.OURS_10C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==10)
            self._load(executionSet, DiagramGenerator.OURS_100C, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==100)
            break # just one execution set

    def toJson(self):
        return json.dumps(self.data)


# Entry point for setup.py
def main():
    rdp = RawDataProcessor()
    rdp.load_all()
    json_txt = rdp.toJson()
    #print json_txt
    
    f = open('/tmp/requests_by_strategies.json', 'w')
    f.write(json_txt)
    f.close()


if __name__ == '__main__':
    main()