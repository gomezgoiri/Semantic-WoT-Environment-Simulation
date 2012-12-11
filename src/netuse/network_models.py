'''
Created on Dec 8, 2012

@author: tulvur
'''

from random import Random
from netuse.nodes import NodeGenerator
from netuse.database.parametrization import Parametrization

class NetworkModelManager(object):
    """
    Class which runs different network models which simulate activity from nodes leaving and joining the network.
    """
    
    @staticmethod
    def run_model(simulation, parametrization=None):
        model = parametrization.network_model
        
        if model==DynamicNodesModel.ID:
            pass
        elif model==ChaoticModel.ID:
            dm = DynamicNodesModel(simulation, parametrization)
            dm.configure()
        else: # model=="normal" or None or invalid
            pass # do nothing


class DynamicNodesModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    ID = Parametrization.dynamic_netmodel
    
    def __init__(self, simulation, parametrization, mean=5000, std_dev=3000):
        self._change_state_each = (mean, std_dev)
        self._simulation = simulation
        self._sim_time = parametrization.simulateUntil
        self._random = Random()
    
    def configure(self):
        for node in NodeGenerator.getNodes():
            last_event_time = 0
            while last_event_time < self._sim_time:
                next_event_on = self._random.normalvariate(*self._change_state_each)
                last_event_time += next_event_on
                
                if last_event_time < self._sim_time:
                    node.swap_state(starts_at=last_event_time, simulation=self._simulation)


class ChaoticModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    ID = Parametrization.chaotic_netmodel
    
    pass