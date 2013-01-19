'''
Created on Sep 16, 2012

@author: tulvur
'''
import weakref
from netuse.nodes import NodeManager
from netuse.triplespace.network.discovery.discovery import DiscoveryInstance
from netuse.triplespace.network.discovery.record import DiscoveryRecordObserver


class MagicInstantNetwork(DiscoveryRecordObserver):
    
    def __init__(self):        
        self.whitepage_exist = False
        self.instances = weakref.WeakSet() # they are also the observers
    
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
    
    def get_whitepage(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        if self.get_my_record().is_whitepage:
            return self.me
        wp_rec = self.magic_network.get_whitepage_record()
        return None if wp_rec is None else self._get_node_for_record( wp_rec ) 
    
    def _get_node_for_record(self, record):
        return NodeManager.getNodeByName(record.node_name)
    
    @property
    def me(self):
        return self._get_node_for_record(self.get_my_record())