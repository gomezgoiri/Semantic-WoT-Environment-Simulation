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

import weakref
from random import Random
from netuse.sim_utils import schedule
from netuse.nodes import NodeManager
from netuse.triplespace.network.discovery.discovery import AbstractDiscoveryFactory, DiscoveryInstance
from netuse.triplespace.network.discovery.record import DiscoveryRecordObserver


class SimpleDiscoveryFactory(AbstractDiscoveryFactory):
    
    def create(self, my_record):
        if not hasattr(self, 'network'):
            self.network = MagicInstantNetwork(self.simulation)
        
        return SimpleDiscoveryMechanism(my_record, self.network)


class MagicInstantNetwork(DiscoveryRecordObserver):
    
    # set up taking into account how long it takes to an Android device
    # to process 300 requests without becoming overloaded and start rejecting them (i.e. causing a TIMEOUT)
    # Can attend 30 requests in 1 second => in 10 seconds processes 300 requests
    NOTIFICATION_LIMIT = 10 * 1000
    
    def __init__(self, simulation):        
        self.whitepage_exist = False
        self.instances = weakref.WeakSet() # they are also the observers
        self.simulation = simulation
        self._random = Random()
    
    def join_space(self, discovery_instance):
        # magic instant observer! without network delays :-P
        discovery_instance.get_my_record().add_change_observer(self)
        self.instances.add(discovery_instance)
        
    def _get_node_for_record(self, record):
        return NodeManager.getNodeByName(record.node_name)
    
    def get_records(self):
        current_records = weakref.WeakSet()
        for instance in self.instances:
            record = instance.get_my_record()
            if not self._get_node_for_record(record).down:
                current_records.add( record )
        return current_records
    
    def get_whitepage_record(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        for instance in self.instances:
            record = instance.get_my_record()
            if not self._get_node_for_record(record).down and record.is_whitepage:
                # TODO unfortunately more than one can coexist, consider it
                return record
        return None
    
    def notify_changes(self):
        wp = self.get_whitepage_record()
        if self.whitepage_exist and wp==None:
            self.whitepage_exist = False
        else:
            if wp!=None:
                self.whitepage_exist = True
                # notifyies on "whitepage_selected_after_none"
                for observer in self.instances:
                    # SimpleDiscoveryMechanism
                    if not observer.me.down:
                        # notify at different moments to avoid the Providers from sending all their clues at the same time
                        delay = 10 + self._random.random() * MagicInstantNetwork.NOTIFICATION_LIMIT
                        self.notify_observer( delay = delay, observer = observer )
                        observer.on_whitepage_selected_after_none()
    
    @schedule
    def notify_observer(self, observer):
        # The notification is delayed a little bit to avoid server overload.
        # This can happen if all the observers start sending their clues at the same time.
        observer.on_whitepage_selected_after_none()


class SimpleDiscoveryMechanism(DiscoveryInstance):
    """
    Simple discovery, which just asks to the MagicInstantNetwork object to get the latest state.
    """
    def __init__(self, my_record, magic_network):
        super(SimpleDiscoveryMechanism, self).__init__()
        self.my_record = my_record
        # If you use weakref in "magic_network": the factory will be destroyed and this will be None.
        self.magic_network = magic_network # weakref.proxy(magic_network) 
        self.magic_network.join_space(self)
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    # paradox: it just intermediates (to avoid directly observing other nodes' registers)
    def on_whitepage_selected_after_none(self):
        for observer in self.observers:
            observer.on_whitepage_selected_after_none()
    
    def get_my_record(self):
        return self.my_record
    
    def get_discovered_records(self):
        if not self.me.down:
            restOfTheRecords = self.magic_network.get_records()
            restOfTheRecords.remove( self.get_my_record() ) # should be there since !me.down
            return restOfTheRecords
        return []        
    
    def get_nodes(self):
        ret = []
        for record in self.get_discovered_records():
            ret.append( self._get_node_for_record(record) )
        return ret
    
    def get_whitepage_record(self):
        if self.get_my_record().is_whitepage:
            return self.get_my_record()
        return self.magic_network.get_whitepage_record() 
    
    def get_whitepage(self):
        wp_rec = self.get_whitepage_record()
        return None if wp_rec is None else self._get_node_for_record( wp_rec ) 
    
    def _get_node_for_record(self, record):
        return NodeManager.getNodeByName(record.node_name)
    
    @property
    def me(self):
        return self._get_node_for_record(self.get_my_record())