'''
Created on Sep 22, 2012

@author: tulvur
'''

import json
from netuse.database.execution import ExecutionSet
from netuse.database.results import NetworkTrace
from netuse.database.parametrization import Parametrization
from netuse.evaluation.number_requests.roles.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
        self.our_100c_filter = lambda p: p.numConsumers==100 and p.strategy==Parametrization.our_solution

    # TODO using **kargs _load_prov2wp(), _load_cons2wp() and _load_cons2prov() can be written just once!
    
    def _load_prov2wp(self, executionSet, additionalFilter=None):
        requests_by_node = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if additionalFilter==None or additionalFilter(execution.parameters):
                
                num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                num_requests = NetworkTrace.objects(execution=execution.id, path__contains="/whitepage/clues/").count()
                if num_nodes not in requests_by_node:
                    requests_by_node[num_nodes] = []
                requests_by_node[num_nodes].append(num_requests)
        
        # sort by num_nodes
        sort = sorted(requests_by_node.items())
        
        self.data[DiagramGenerator.PROV_WP] = {}
        self.data[DiagramGenerator.PROV_WP][DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        self.data[DiagramGenerator.PROV_WP][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
        
    def _load_cons2wp(self, executionSet, additionalFilter=None):
        requests_by_node = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if additionalFilter==None or additionalFilter(execution.parameters):
                
                num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                num_requests = NetworkTrace.objects(execution=execution.id, path__exact="/whitepage/clues").count()
                if num_nodes not in requests_by_node:
                    requests_by_node[num_nodes] = []
                requests_by_node[num_nodes].append(num_requests)
        
        # sort by num_nodes
        sort = sorted(requests_by_node.items())
        
        self.data[DiagramGenerator.CONS_WP] = {}
        self.data[DiagramGenerator.CONS_WP][DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        self.data[DiagramGenerator.CONS_WP][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
        
    def _load_cons2prov(self, executionSet, additionalFilter=None):
        requests_by_node = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if additionalFilter==None or additionalFilter(execution.parameters):
                
                num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                num_requests = NetworkTrace.objects(execution=execution.id, path__startswith="/spaces/").count()
                if num_nodes not in requests_by_node:
                    requests_by_node[num_nodes] = []
                requests_by_node[num_nodes].append(num_requests)
        
        # sort by num_nodes
        sort = sorted(requests_by_node.items())
        
        self.data[DiagramGenerator.CONS_PROV] = {}
        self.data[DiagramGenerator.CONS_PROV][DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        self.data[DiagramGenerator.CONS_PROV][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
    
    def load_all(self):
        for executionSet in ExecutionSet.objects(experiment_id='network_usage').get_simulated():
            self._load_prov2wp(executionSet, additionalFilter=self.our_100c_filter)
            self._load_cons2wp(executionSet, additionalFilter=self.our_100c_filter)
            self._load_cons2prov(executionSet, additionalFilter=self.our_100c_filter)
            break # just one execution set

    def toJson(self):
        return json.dumps(self.data)


# Entry point for setup.py
def main():
    rdp = RawDataProcessor()
    rdp.load_all()
    json_txt = rdp.toJson()
    #print json_txt
    
    f = open('/tmp/requests_by_roles.json', 'w')
    f.write(json_txt)
    f.close()


if __name__ == '__main__':
    main()