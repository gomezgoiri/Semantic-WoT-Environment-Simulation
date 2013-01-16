'''
Created on Jan 15, 2013

@author: tulvur
'''
import weakref
from abc import ABCMeta, abstractmethod


class DiscoveryFactory(object):
    
    def __init__(self, nodes):
        # Dirty. If it is imported at the beginning of the module, it throws a recursion error
        from netuse.triplespace.network.discovery.simple import MagicInstantNetwork
        self.network = MagicInstantNetwork(nodes)
        
    def create_simple_discovery(self, localNode, my_record):
        # Dirty. If it is imported at the beginning of the module, it throws a recursion error
        from netuse.triplespace.network.discovery.simple import SimpleDiscoveryMechanism
        return SimpleDiscoveryMechanism(localNode, self.network)


class DiscoveryEventObserver(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def on_whitepage_selected_after_none(self):
        '''
        When no whitepage existed in the space and a new one has been selected.
        '''
        pass

class DiscoveryInstance(object):
    """
    Simple discovery, which just asks to the MagicInstantNetwork object to get the latest state.
    """
    __metaclass__ = ABCMeta
    
    
    def __init__(self):
        self.observers = weakref.WeakSet()
            
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