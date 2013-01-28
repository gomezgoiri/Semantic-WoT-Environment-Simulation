'''
Created on Jan 08, 2013

@author: tulvur
'''

import json
from netuse.database.execution import ExecutionSet
from netuse.database.results import HTTPTrace
from netuse.network_models import NetworkModelManager
from netuse.database.parametrization import Parametrization
from netuse.evaluation.dynamism.diagram import DiagramGenerator

class RawDataProcessor(object):

    def __init__(self):
        self.data = {}
        
    def _load(self, executionSet, name, strategy):
        requests_by_interval = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if execution.parameters.strategy==strategy:
                net_model = execution.parameters.network_model
                interval = None
                if net_model.type==NetworkModelManager.normal_netmodel:#onedown_netmodel:
                    interval = 3600000 # aka never
                else:
                    interval = net_model.state_change_mean
                
                if interval not in requests_by_interval:
                    requests_by_interval[interval] = []
                
                num_requests = HTTPTrace.objects(execution=execution.id).count()
                requests_by_interval[interval].append(num_requests) 
        
        # sort by num_nodes
        sort = sorted(requests_by_interval.items())
        
        self.data[name] = {}
        self.data[name][DiagramGenerator.DROP_INTERVAL] = [e[0] for e in sort]
        self.data[name][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
        
    def _load_by_communication_pattern(self, executionSet, name, strategy, **trace_pattern):
        requests_by_interval = {} # tuples of 2 elements: number of nodes in the simulation and requests
        for execution in executionSet.executions:
            if execution.parameters.strategy==strategy:
                net_model = execution.parameters.network_model
                interval = None
                if net_model.type==NetworkModelManager.normal_netmodel:#onedown_netmodel:
                    interval = 3600000 # aka never
                else:
                    interval = net_model.state_change_mean
                
                if interval not in requests_by_interval:
                    requests_by_interval[interval] = []
                
                num_requests = HTTPTrace.objects(execution=execution.id, **trace_pattern).count()
                requests_by_interval[interval].append(num_requests) 
        
        # sort by num_nodes
        sort = sorted(requests_by_interval.items())
        
        self.data[name] = {}
        self.data[name][DiagramGenerator.DROP_INTERVAL] = [e[0] for e in sort]
        self.data[name][DiagramGenerator.REQUESTS] = [e[1] for e in sort]
        
    def merge(self, data_serie1, data_serie2):
        assert data_serie1[DiagramGenerator.DROP_INTERVAL] == data_serie2[DiagramGenerator.DROP_INTERVAL]
        
        ret = {}
        ret[DiagramGenerator.DROP_INTERVAL] = []
        ret[DiagramGenerator.REQUESTS] = []
        
        for drop, data1, data2 in zip(data_serie1[DiagramGenerator.DROP_INTERVAL], # or data_serie2
                                        data_serie1[DiagramGenerator.REQUESTS],
                                        data_serie2[DiagramGenerator.REQUESTS] ):
            ret[DiagramGenerator.DROP_INTERVAL].append( drop )
            execution = []
            for da1, da2 in zip(data1, data2):
                execution.append( da1 + da2 )
            ret[DiagramGenerator.REQUESTS].append( execution )
        return ret
        
    
    def load_all(self):
        for executionSet in ExecutionSet.objects(experiment_id='dynamism').get_simulated():
            self._load(executionSet, DiagramGenerator.NB, Parametrization.negative_broadcasting)
            self._load(executionSet, DiagramGenerator.OURS, Parametrization.our_solution)
            self._load_by_communication_pattern(executionSet, DiagramGenerator.CONS_PROV, Parametrization.our_solution,
                                                path__startswith="/spaces/")            
            self._load_by_communication_pattern(executionSet, DiagramGenerator.PROV_WP, Parametrization.our_solution,
                                                path__contains="/whitepage/clues/")
            
            # communication between Consumers and Whitepage follow 2 different patterns
            self._load_by_communication_pattern(executionSet, "tmp", Parametrization.our_solution,
                                                path__exact="/whitepage/choose")
            self._load_by_communication_pattern(executionSet, "tmp2", Parametrization.our_solution,
                                                path__exact="/whitepage/clues")
            self.data[DiagramGenerator.CONS_WP] = self.merge( self.data["tmp"], self.data["tmp2"] )
            del self.data["tmp"]
            del self.data["tmp2"]
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