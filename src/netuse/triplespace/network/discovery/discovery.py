'''
Created on Jan 15, 2013

@author: tulvur
'''
import weakref
from abc import ABCMeta, abstractmethod


class DiscoveryFactory(object):
    
    SIMPLE_DISCOVERY = "simple"
    MDNS_DISCOVERY = "mdns"
    
    def __init__(self, simulation):
        self.simulation = simulation
        
    def create_simple(self, my_record):
        # Dirty. If it is imported at the beginning of the module, it throws a recursion error
        if not hasattr(self, 'network'):
            from netuse.triplespace.network.discovery.simple import MagicInstantNetwork
            self.network = MagicInstantNetwork()
        
        from netuse.triplespace.network.discovery.simple import SimpleDiscoveryMechanism
        return SimpleDiscoveryMechanism(my_record, self.network)
    
    def create_mdns(self, my_record, simulation):
        # Dirty. If it is imported at the beginning of the module, it throws a recursion error
        if not hasattr(self, 'network'):
            from netuse.mdns.network import UDPNetwork
            self.network = UDPNetwork(self.simulation, udp_tracer = None)
        
        from netuse.triplespace.network.discovery.mdns import MDNSDiscoveryInstance
        return MDNSDiscoveryInstance(my_record, self.network, self.simulation)


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