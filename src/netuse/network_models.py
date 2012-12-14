'''
Created on Dec 8, 2012

@author: tulvur
'''

from random import Random
from SimPy.Simulation import Process, hold
from netuse.sim_utils import activatable
from netuse.nodes import NodeGenerator

class NetworkModelManager(object):
    """
    Class which runs different network models which simulate activity from nodes leaving and joining the network.
    """
        
    # network models
    normal_netmodel = "normal"
    dynamic_netmodel = "dynamic"
    chaotic_netmodel = "chaos"
    
    @staticmethod
    def run_model(simulation, parametrization, network):
        model = parametrization.network_model
        
        if model==NetworkModelManager.dynamic_netmodel:
            dm = DynamicNodesModel(simulation, parametrization)
            dm.configure()
        elif model==NetworkModelManager.chaotic_netmodel:
            cm = ChaoticModel(simulation, network)
            cm.run(at=0)
        else: # model=="normal" or None or invalid
            pass # do nothing


class DynamicNodesModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    def __init__(self, parametrization, mean=5000, std_dev=3000):
        self._change_state_each = (mean, std_dev)
        self._sim_time = parametrization.simulateUntil
        self._random = Random()
    
    def configure(self):
        for node in NodeGenerator.getNodes():
            last_event_time = 0
            while last_event_time < self._sim_time:
                next_event_on = self._random.normalvariate(*self._change_state_each)
                last_event_time += next_event_on
                
                if last_event_time < self._sim_time:
                    node.swap_state(at=last_event_time)


class ChaoticModel(Process):
    """
    A Model where the whitepage goes down and up periodically.
    """
    
    def __init__(self, simulation, network, mean=5000, std_dev=3000):
        super(ChaoticModel, self).__init__(sim=simulation)
        self._change_state_each = (mean, std_dev)
        self._network = network # type: MagicInstantNetwork
        self._random = Random()
    
    @activatable
    def run(self):
        last_wp = None
        while True:            
            next_event_on = 0
            while next_event_on <= 0: # ignore delays with negative values!
                next_event_on = self._random.normalvariate(*self._change_state_each)
            yield hold, self, next_event_on
            
            if last_wp is not None:
                last_wp.swap_state() # to revert the going down of the previous WP
            
            last_wp = self._network.get_whitepage()
            if last_wp is not None:
                last_wp.swap_state() # normal call, not scheduling it
                print "%s went down."%(last_wp.name)