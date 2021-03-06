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

from random import Random
from SimPy.Simulation import Process, hold
from netuse.sim_utils import activatable
from netuse.nodes import NodeManager

class NetworkModelManager(object):
    """
    Class which runs different network models which simulate activity from nodes leaving and joining the network.
    """
        
    # network models
    normal_netmodel = "normal"
    dynamic_netmodel = "dynamic"
    onedown_netmodel = "onedown"
    chaotic_netmodel = "chaos"
    
    @staticmethod
    def run_model(simulation, parametrization, network):
        # parametrization should be a netuse.database.parametrization.NetworkModel
        model = parametrization.network_model.type
        
        if model==NetworkModelManager.dynamic_netmodel:
            # parametrization is a ParametrizableNetworkModel
            dm = DynamicNodesModel(parametrization.simulateUntil,
                              parametrization.network_model.state_change_mean,
                              parametrization.network_model.state_change_std_dev)
            dm.configure()
        elif model==NetworkModelManager.onedown_netmodel:
            # parametrization is a ParametrizableNetworkModel
            dm = OneNodeDownModel(parametrization.simulateUntil,
                              parametrization.network_model.state_change_mean,
                              parametrization.network_model.state_change_std_dev)
            dm.configure()
        elif model==NetworkModelManager.chaotic_netmodel:
            # parametrization is a ParametrizableNetworkModel
            cm = ChaoticModel(simulation,
                              parametrization.network_model.state_change_mean,
                              parametrization.network_model.state_change_std_dev)
            cm.run(at=0)
        else: # model=="normal" or None or invalid
            pass # do nothing


class DynamicNodesModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    def __init__(self, simulation_time, mean_state_change, std_dev_state_change):
        self._change_state_each = (mean_state_change, std_dev_state_change)
        self._sim_time = simulation_time
        self._random = Random()
    
    def configure(self):
        for node in NodeManager.getNodes():
            last_event_time = 0
            while last_event_time < self._sim_time:
                next_event_on = self._random.normalvariate(*self._change_state_each)
                last_event_time += next_event_on
                
                if last_event_time < self._sim_time:
                    node.swap_state(at=last_event_time)


class OneNodeDownModel(object):
    """
    A Model where one node EACH TIME goes down and up periodically.
    """
    
    def __init__(self, simulation_time, mean_state_change, std_dev_state_change):
        self._change_state_each = (mean_state_change, std_dev_state_change)
        self._sim_time = simulation_time
        self._random = Random()
    
    def configure(self):
        nodes = NodeManager.getNodes()
        node = None
        event_at = 0
        while event_at < self._sim_time:
            next_event_on = self._random.normalvariate(*self._change_state_each)
            event_at += next_event_on
            if event_at < self._sim_time:
                # the node choosen in the previous loop goes up
                if node is not None:
                    node.swap_state(at=event_at)
                # select a new node which will go down
                node = self._random.choice(nodes)
                node.swap_state(at=event_at)


class ChaoticModel(Process):
    """
    A Model where the whitepage goes down and up periodically.
    """
    
    def __init__(self, simulation, mean_wp_down, std_dev_wp_down):
        super(ChaoticModel, self).__init__(sim=simulation)
        self._change_state_each = (mean_wp_down, std_dev_wp_down)
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
                #print "%s went up on %d."%(last_wp.name, self.sim.now())
            last_wp = self.find_whitepage()
            if last_wp is not None:
                last_wp.swap_state() # normal call, not scheduling it
                #print "%s went down on %d."%(last_wp.name, self.sim.now())
    
    def find_whitepage(self):
        for node in NodeManager.getNodes():
            record = node._discovery_instance.get_my_record()
            if not node.down and record.is_whitepage:
                return node
        return None