'''
Created on Dec 8, 2012

@author: tulvur
'''

import random
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
    
    def __init__(self, simulation, parametrization):
        self.change_state_each = (5000, 3000) # (mean, std_dev)
        self.simulation = simulation
        self.sim_time = parametrization.simulateUntil
    
    def configure(self):
        for node in NodeGenerator.getNodes():
            last_event_time = 0
            while last_event_time < self.sim_time:
                next_event_on = random.normalvariate(*self.change_state_each)
                last_event_time += next_event_on
                
                if last_event_time < self.sim_time:
                    node.swap_state(starts_at=last_event_time, simulation=self._simulation)


class ChaoticModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    ID = Parametrization.chaotic_netmodel
    
    pass