'''
Created on Jan 17, 2013

@author: tulvur
'''
from clueseval.clues.versions.management import Version
from netuse.nodes import NodeManager
from netuse.mdns.network import MDNSNode
from netuse.mdns.record import PTRRecord, SVRRecord, TXTRecord
from netuse.triplespace.network.discovery.discovery import DiscoveryInstance
from netuse.triplespace.network.discovery.record import DiscoveryRecord, DiscoveryRecordObserver

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
        self.start_mdns_node(udp_network)
        # If you use weakref in "udp_network": the factory will be destroyed and this will be None.
        self.udp_network = udp_network # weakref.proxy(magic_network) 
        self.udp_network.join_space(self)
    
    def start_mdns_node(self, udp_network, simulation):
        self.mdns_node = MDNSNode( node_id = self.my_record.node_name,
                                   udp_network = udp_network,
                                   simulation = simulation )
        #write my registers
        domain_name = self.my_record.node_name+ "._http._tcp.local"
        self.mdns_node.write_record( PTRRecord("_http._tcp.local", domain_name) )
        self.mdns_node.write_record( SVRRecord(domain_name, "0.0.0.0", 9999) )
        self.mdns_node.write_record( DiscoveryRecordConverter.to_txt_record(self.my_record) )
        
        
    # stop() when node goes down!
    
    def start(self):
        self.mdns_node.start()
    
    def stop(self):
        self.mdns_node.stop()
    
    # inherited from DiscoveryRecordObserver
    def notify_changes(self):
        # rewrites into the cache
        self.mdns_node.write_record( DiscoveryRecordConverter.to_txt_record(self.my_record) )
    
    # TODO or delete!
    def on_whitepage_selected_after_none(self):
        pass
    
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
        if self.get_my_record().is_whitepage:
            return self.get_my_record()
        
        for record in self.mdns_node.cache.records:
            if record.type=="TXT":
                if record.keyvalues['iw']:
                    return DiscoveryRecordConverter.to_discovery_record(record)
        
        return None
    
    def get_whitepage(self):
        wp_r = self.get_whitepage_record()
        
        if wp_r is None: return None
        return self._get_node_for_record( wp_r )
    
    def _get_node_for_record(self, record):
        return NodeManager.getNodeByName(record.node_name)
    
    @property
    def me(self):
        return self._get_node_for_record(self.get_my_record())