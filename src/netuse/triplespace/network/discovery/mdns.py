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

from SimPy.Simulation import Process, SimEvent, waitevent
from clueseval.clues.versions.management import Version
from netuse.results import G
from netuse.nodes import NodeManager
from netuse.mdns.network import UDPNetwork, MDNSNode
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord
from netuse.triplespace.network.discovery.discovery import AbstractDiscoveryFactory, DiscoveryInstance
from netuse.triplespace.network.discovery.record import DiscoveryRecord, DiscoveryRecordObserver


class MDNSDiscoveryFactory(AbstractDiscoveryFactory):
    
    def create(self, my_record):
        if not hasattr(self, 'network'):
            self.network = UDPNetwork(self.simulation, udp_tracer = G._udp_tracer)
        
        return MDNSDiscoveryInstance(my_record, self.network, self.simulation)


class DiscoveryRecordConverter(object):
    
    @staticmethod
    def to_txt_record(discovery_record):
        keyvalues = {}
        keyvalues['m'] = "%d%s"%discovery_record.memory
        keyvalues['s'] = "%d%s"%discovery_record.storage
        keyvalues['js'] = discovery_record.joined_since
        keyvalues['bl'] = discovery_record.battery_lifetime
        keyvalues['iw'] = discovery_record.is_whitepage
        if discovery_record.version is not None:
            keyvalues['g'] = discovery_record.version.generation
            keyvalues['v'] = discovery_record.version.version
        name = discovery_record.node_name + "._http._tcp.local"
        return TXTRecord(name, keyvalues)
    
    @staticmethod
    def to_discovery_record(txt_record):
        node_name = txt_record.name.split("._http._tcp.local")[0]
        dr = DiscoveryRecord( node_name,
                                memory = txt_record.keyvalues['m'],
                                storage = txt_record.keyvalues['s'],
                                joined_since = txt_record.keyvalues['js'],
                                battery_lifetime = txt_record.keyvalues['bl'],
                                is_whitepage = txt_record.keyvalues['iw'] )
        
        if 'g' in txt_record.keyvalues and 'v' in txt_record.keyvalues:
            dr.version = Version( generation = txt_record.keyvalues['g'],
                                  version = txt_record.keyvalues['v'] )
        return dr


class MDNSDiscoveryInstance(DiscoveryInstance, DiscoveryRecordObserver):
    """
    Uses mDNS discovery.
    """
    def __init__(self, my_record, udp_network, simulation):
        super(MDNSDiscoveryInstance, self).__init__()
        self.my_record = my_record
        self.my_record.add_change_observer(self)
        
        # If you use weakref in "udp_network": the factory will be destroyed and this will be None.
        self.udp_network = udp_network # weakref.proxy(magic_network) 
        self.simulation = simulation
        
        self.start_mdns_node(udp_network)
    
    def start_mdns_node(self, udp_network):
        self.mdns_node = MDNSNode( node_id = self.my_record.node_name,
                                   udp_network = udp_network,
                                   simulation = self.simulation )
        #write my registers
        domain_name = self.my_record.node_name+ "._http._tcp.local"
        self.mdns_node.write_record( PTRRecord("_http._tcp.local", domain_name) )
        self.mdns_node.write_record( SVRRecord(domain_name, "0.0.0.0", 9999) )
        self.mdns_node.write_record( DiscoveryRecordConverter.to_txt_record(self.my_record) )
        
        self.detector = NewWPDetector(self, self.simulation) # maybe I should do a mechanism to stop it...
        self.simulation.activate( self.detector, self.detector.check_new_wps() )
        
        self.mdns_node.add_observer( self.detector )
    
    def start(self):
        self.mdns_node.start()
    
    def stop(self):
        self.mdns_node.stop()
    
    # inherited from DiscoveryRecordObserver
    def notify_changes(self):
        # rewrites into the cache
        self.mdns_node.write_record( DiscoveryRecordConverter.to_txt_record(self.my_record) )
    
    
    def notify_whitepage_changed(self):
        for observer in self.observers:
            observer.on_whitepage_selected_after_none()
    
    def get_my_record(self):
        return self.my_record
    
    def get_discovered_records(self):
        if self.mdns_node.running: # self.me.down:
            restOfTheRecords = []
            for record in self.mdns_node.cache.records:
                if record.type=="TXT":
                    dr = DiscoveryRecordConverter.to_discovery_record(record)
                    restOfTheRecords.append(dr)
            return restOfTheRecords
        return []        
    
    def get_nodes(self):
        ret = []
        for record in self.get_discovered_records():
            ret.append( self._get_node_for_record(record) )
        return ret
    
    def get_whitepage_record(self):
        last_whitepage = None
        if self.get_my_record().is_whitepage:
            last_whitepage = self.get_my_record()
        
        # if more than 1 records are marked as WP, we choose the last one
        for record in self.mdns_node.cache.records:
            if record.type=="TXT":
                if record.keyvalues['iw']:
                    if last_whitepage is None:
                        last_whitepage = DiscoveryRecordConverter.to_discovery_record(record)
                    else:
                        possible_whitepage = DiscoveryRecordConverter.to_discovery_record(record)
                        if last_whitepage.version < possible_whitepage.version:
                            last_whitepage = possible_whitepage
        
        return last_whitepage
    
    def get_whitepage(self):
        wp_r = self.get_whitepage_record()
        
        if wp_r is None: return None
        return self._get_node_for_record( wp_r )
    
    def _get_node_for_record(self, record):
        return NodeManager.getNodeByName(record.node_name)
    
    @property
    def me(self):
        return self._get_node_for_record(self.get_my_record())


class NewWPDetector(Process):
    
    def __init__(self, mdns_instance, sim):
        super(NewWPDetector, self).__init__( sim = sim )
        self.instance = mdns_instance
        self.last_wp_name = None
        self.__new_record_update = SimEvent(name="new_record_updated", sim=sim)
    
    def check_new_wps(self):
        while True:
            wp_r = self.instance.get_whitepage_record()
            if wp_r is not None:
                new_name = wp_r.node_name
                if self.last_wp_name != new_name:
                    self.instance.notify_whitepage_changed()
                    self.last_wp_name = new_name
            yield waitevent, self, (self.__new_record_update,)
    
    def notify_txt_record(self, record):
        if "iw" in record.keyvalues:
            self.__new_record_update.signal()