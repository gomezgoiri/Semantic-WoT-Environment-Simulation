# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import json
from netuse.database.execution import ExecutionSet
from netuse.database.results import HTTPTrace
from netuse.database.parametrization import Parametrization
from netuse.evaluation.number_requests.roles.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
        self.our_100c_filter = lambda p: p.numConsumers==100 and p.strategy==Parametrization.our_solution
      
    def _load_by_communication_pattern(self,  executionSet, additionalFilter=None, **trace_pattern):
        requests_by_node = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if additionalFilter==None or additionalFilter(execution.parameters):
                
                num_nodes = len(execution.parameters.nodes) # in the reference of mongoengine, they defend this method
                num_requests = HTTPTrace.objects(execution=execution.id, **trace_pattern).count()
                if num_nodes not in requests_by_node:
                    requests_by_node[num_nodes] = []
                requests_by_node[num_nodes].append(num_requests)
        
        # sort by num_nodes
        sort = sorted(requests_by_node.items())
        
        ret = {}
        ret[DiagramGenerator.NUM_NODES] = [e[0] for e in sort]
        ret[DiagramGenerator.REQUESTS] = [e[1] for e in sort]
        return ret
    
    def load_all(self):
        for executionSet in ExecutionSet.objects(experiment_id='network_usage').get_simulated():
            # provider to whitepage
            self.data[DiagramGenerator.PROV_WP] =
                                    self._load_by_communication_pattern(self, executionSet,
                                                                            additionalFilter=self.our_100c_filter,
                                                                            path__contains="/whitepage/clues/")
            # consumer to whitepage
            self.data[DiagramGenerator.CONS_WP] =
                                    self._load_by_communication_pattern(self, executionSet,
                                                                            additionalFilter=self.our_100c_filter,
                                                                            path__exact="/whitepage/clues")
            # consumer to provider
            self.data[DiagramGenerator.CONS_PROV] =
                                    self._load_by_communication_pattern(self, executionSet,
                                                                            additionalFilter=self.our_100c_filter,
                                                                            path__startswith="/spaces/")
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