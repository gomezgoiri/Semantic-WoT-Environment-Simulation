'''
Created on Jan 12, 2013

@author: tulvur
'''

from netuse.mdns.cache import Cache
from netuse.mdns.responder import Responder
from netuse.mdns.querier import ContinuousQuerier
from netuse.mdns.record import PTRRecord
from netuse.mdns.packet import DNSPacket, Query, SubQuery

class UDPNetwork(object):
    
    def __init__(self):
        self.mdns_nodes = {}   
    
    def join(self, node, node_id):
        self.mdns_nodes[node_id] = node
    
    def send_multicast(self, dns_packet):
        for mdns_node in self.mdns_nodes.itervalues():
            if mdns_node.running:
                mdns_node.receive_packet(dns_packet)
            
    def send_unicast(self, node_id, dns_packet):
        mdns_node = self.mdns_nodes[node_id]
        if mdns_node.running:
            mdns_node.receive_packet(dns_packet)

    

class MDNSNode(object):
    
    def __init__(self, udp_network, sim):
        self.udp_network = udp_network
        self.initialized = False
        self.running = False
        
        self.responder = Responder(sim)
        self.cache = Cache(sim, self) # observer with renew_record method
        browsing_subquery = SubQuery(name = "_services._dns-sd._udp.local", record_type="PTR")
        self.browser = ContinuousQuerier(browsing_subquery, sim, self)
    
    def start(self):
        """On set up."""
        self.running = True
        self.browser.reset()
        if not self.initialized:
            self.sim.activate(self.cache, self.cache.wait_for_next_event())
            self.sim.activate(self.responder, self.responder.answer())
        # continuous queries is the only object which needs to be restarted
        self.sim.activate(self.browser, self.browser.query_continuously())
        self.initialized = True # a flag for the first time start() is called
    
    def stop(self):
        """Call when it goes down for whatever reason."""
        self.browser.stop()
        # no need to stop the responder:
        # 1) UDPNetwork will ask this node anything.
        # 2) Outgoing communications are also avoided in send_xcast methods
        
        # will all the events flushed, the cache will simply waits
        # until the node goes up to start caching again
        self.cache.flush_all()
        self.running = False
        
    def receive_packet(self, dns_packet):
        if dns_packet.type == DNSPacket.TYPE_QUERY:
            # dns_packet.data is a Query object
            self.cache.queue_query( dns_packet.data )
        elif dns_packet.type == DNSPacket.TYPE_RESPONSE:
            # dns_packet.data is a List of Record objects
            for record in dns_packet.data:
                self.responder.cache_record( record )
    
    # cache observer
    def renew_record(self, record_to_renew):
        sq = SubQuery( name = record_to_renew.name, record_type = record_to_renew.type )
        self.send_query(sq, query_type="QM")
    
    # used by ContinuousQuerier and by self.renew_record
    def send_query(self, unique_subquery, query_type): # queries always through multicast
        q = Query( queries = (unique_subquery,), known_answers= self.cache.get_known_answers() )
        self.send_multicast( DNSPacket(ttype=DNSPacket.TYPE_QUERY, data=q) )
    
    # used by send_query and Responder
    def send_multicast(self, dns_packet):
        if self.running:
            self.network.send_multicast(dns_packet)
    
    # used by Responder        
    def send_unicast(self, node_id, dns_packet):
        if self.running:
            self.network.send_unicast(node_id, dns_packet)