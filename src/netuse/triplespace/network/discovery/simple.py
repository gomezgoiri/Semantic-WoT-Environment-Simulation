'''
Created on Sep 16, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
import weakref
from netuse.triplespace.network.discovery.record import DiscoveryRecordObserver


class DiscoveryFactory(object):
    
    def __init__(self, nodes):
        self.network = MagicInstantNetwork(nodes)
        
    def create_simple_discovery(self, localNode):
        return SimpleDiscoveryMechanism(localNode, self.network)


class MagicInstantNetwork(DiscoveryRecordObserver):
    
    def __init__(self, nodes):
        self.nodes = nodes
        for node in self.nodes:
            # magic instant observer! without network delays :-P
            node.discovery_record.add_change_observer(self)
        
        self.whitepage_exist = False
        self.observers = weakref.WeakSet()
    
    def add_changes_observer(self, observer):
        self.observers.add(observer)
    
    def get_nodes(self):
        current_nodes = weakref.WeakSet()
        for node in self.nodes:
            if not node.down:
                current_nodes.add( node )
        return current_nodes
    
    def get_whitepage(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        for node in self.nodes:
            if not node.down and node.discovery_record.is_whitepage:
                # TODO unfortunately more than one can coexist, consider it
                return node
        return None
    
    def notify_changes(self):
        wp = self.get_whitepage()
        if not self.whitepage_exist:
            if wp!=None:
                self.whitepage_exist = True
                # notifyies on "whitepage_selected_after_none"
                for observer in self.observers:
                    # SimpleDiscoveryMechanism
                    if not observer.me.down:
                        observer.on_whitepage_selected_after_none()
        else:
            if wp==None:
                self.whitepage_exist = False


class SimpleDiscoveryObserver(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def on_whitepage_selected_after_none(self):
        '''
        When no whitepage existed in the space and a new one has been selected.
        '''
        pass


class SimpleDiscoveryMechanism(object):
    """
    Simple discovery, which just asks to the MagicInstantNetwork object to get the latest state.
    """
    def __init__(self, me, magic_network):
        self.me_ref = weakref.ref(me) # with a weakref.proxy a WeakSet.remove does not work OK
        self.magic_network = weakref.proxy(magic_network)
        self.magic_network.add_changes_observer(self)
        self.observers = weakref.WeakSet()
            
    def add_changes_observer(self, observer):
        self.observers.add(observer)
    
    # paradox: it just intermediates (to avoid directly observing other nodes' registers)
    def on_whitepage_selected_after_none(self):
        for observer in self.observers:
            observer.on_whitepage_selected_after_none()
    
    def get_nodes(self):
        if not self.me.down:
            restOfTheNodes = self.magic_network.get_nodes()
            restOfTheNodes.remove(self.me) # should be there since !me.down
            return restOfTheNodes
        return []
    
    def get_whitepage(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        if self.me.discovery_record.is_whitepage:
            return self.me
        return self.magic_network.get_whitepage()
    
    @property
    def me(self):
        return self.me_ref()