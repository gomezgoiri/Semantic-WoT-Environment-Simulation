'''
Created on Jan 08, 2013

@author: tulvur
'''

import json
from netuse.database.execution import ExecutionSet
from netuse.database.results import NetworkTrace
from netuse.network_models import NetworkModelManager
from netuse.database.parametrization import Parametrization
from netuse.evaluation.dynamism.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
        
    def _load(self, executionSet, name, strategy, additionalFilter=None):
        requests_by_interval = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if execution.parameters.strategy==strategy:
                net_model = execution.parameters.network_model
                interval = None
                if net_model.type==NetworkModelManager.normal_netmodel:#onedown_netmodel:
                    interval = 9000000 # aka never
                else:
                    interval = net_model.state_change_mean
                
                if interval not in requests_by_interval:
                    requests_by_interval[interval] = []
                
                num_requests = NetworkTrace.objects(execution=execution.id).count()
                requests_by_interval[interval].append(num_requests)
        
        # sort by num_nodes
        sort = sorted(requests_by_interval.items())
        
        self.data[name] = {}
        self.data[name][DiagramGenerator.DROP_INTERVAL] = [e[0] for e in sort]
        self.data[name][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
    
    def load_all(self):
        for executionSet in ExecutionSet.objects(experiment_id='dinamism').get_simulated():
            self._load(executionSet, DiagramGenerator.NB, Parametrization.negative_broadcasting)
            self._load(executionSet, DiagramGenerator.OURS, Parametrization.our_solution, additionalFilter=lambda p: p.numConsumers==1)
            break # just one execution set

    def toJson(self):
        return json.dumps(self.data)


# Entry point for setup.py
def main():
    rdp = RawDataProcessor()
    rdp.load_all()
    json_txt = rdp.toJson()
    #print json_txt
    
    f = open('/tmp/dynamism.json', 'w')
    f.write(json_txt)
    f.close()


if __name__ == '__main__':
    main()