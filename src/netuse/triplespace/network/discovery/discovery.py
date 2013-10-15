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
from abc import ABCMeta, abstractmethod


class DiscoveryFactory(object):
    
    SIMPLE_DISCOVERY = "simple"
    MDNS_DISCOVERY = "mdns"
    
    @staticmethod
    def create(ttype, simulation):
        # Dirty. If it is imported at the beginning of the module, it throws a recursion error
        if ttype == DiscoveryFactory.SIMPLE_DISCOVERY:
            from netuse.triplespace.network.discovery.simple import SimpleDiscoveryFactory
            return SimpleDiscoveryFactory( simulation )
        elif ttype == DiscoveryFactory.MDNS_DISCOVERY:
            from netuse.triplespace.network.discovery.mdns import MDNSDiscoveryFactory
            return MDNSDiscoveryFactory( simulation )
        else:
            raise Exception( "Unacceptable discovery type: %s." % ttype )


class AbstractDiscoveryFactory(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, simulation):
        self.simulation = simulation
    
    @abstractmethod
    def create(self, my_record, tracer = None):
        pass

class DiscoveryEventObserver(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def on_whitepage_selected_after_none(self):
        '''
        DEPRECATED: When no whitepage existed in the space and a new one has been selected.
        The notation has slightly changed, now it means "on new whitepage detected"
        '''
        pass

class DiscoveryInstance(object):
    """
    Simple discovery, which just asks to the MagicInstantNetwork object to get the latest state.
    """
    __metaclass__ = ABCMeta
    
    
    def __init__(self):
        self.observers = weakref.WeakSet()
        
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
            
    def add_changes_observer(self, observer):
        self.observers.add(observer) # of type DiscoveryEventObserver
    
    @abstractmethod
    def get_my_record(self):
        # TODO overlaps with get_nodes, should substitute it in the future
        pass
    
    @abstractmethod
    def get_discovered_records(self):
        # TODO overlaps with get_nodes, should substitute it in the future
        pass
    
    @abstractmethod
    def get_nodes(self):
        pass
    
    @abstractmethod
    def get_whitepage(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        pass
    
    @abstractmethod
    def get_whitepage_record(self):
        '''Returns the record of the node currently acting as whitepage. None if no whitepage exists in the space.'''
        pass