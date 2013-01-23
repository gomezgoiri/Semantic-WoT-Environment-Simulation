'''
Created on Jan 12, 2013

@author: tulvur
'''

import weakref
from netuse.mdns.cache import Cache
from netuse.mdns.responder import Responder
from netuse.mdns.querier import ContinuousQuerier
from netuse.mdns.packet import DNSPacket, Query, SubQuery

class UDPNetwork(object):
    
    def __init__(self, simulation, udp_tracer = None):
        self.simulation = simulation
        self.udp_tracer = udp_tracer
        self.mdns_nodes = {} # key: node (redefined __eq__ and __hash__)
    
    def join(self, node):
        self.mdns_nodes[node.node_id] = node
    
    def send_multicast(self, from_node, dns_packet):
        if self.udp_tracer is not None:
            if dns_packet.type == DNSPacket.TYPE_QUERY:
                self.udp_tracer.trace_query(self.simulation.now(), from_node, dns_packet.data)
            else:
                self.udp_tracer.trace_multicast_response(self.simulation.now(), from_node, dns_packet.data)
            
        for node_id, mdns_node in self.mdns_nodes.iteritems():
            if mdns_node.running and node_id != from_node:
                mdns_node.receive_packet(dns_packet)
            
    def send_unicast(self, from_node, to_node, dns_packet):
        # trace it even if "to_node" does not receive the packet
        if self.udp_tracer is not None:
            self.udp_tracer.trace_unicast_response(self.simulation.now(), from_node, dns_packet.data, to_node)
        
        mdns_node = self.mdns_nodes[to_node]
        if mdns_node.running:
            mdns_node.receive_packet(dns_packet)
    

class MDNSNode(object):
    
    def __init__(self, node_id, udp_network, simulation):
        self.node_id = node_id
        self.udp_network = udp_network
        self.simulation = simulation
        
        self.initialized = False
        self.running = False
        
        self.responder = Responder( sim = self.simulation, sender = self )
        self.cache = Cache( sim = self.simulation, record_observer = self ) # observer with renew_record method
        browsing_subquery = SubQuery( name = "_services._dns-sd._udp.local", record_type = "PTR" )
        self.browser = ContinuousQuerier( browsing_subquery, sim = self.simulation , sender = self )
        
        self.txt_observers = weakref.WeakSet() # normally just one
    
    def add_observer(self, observer):
        self.txt_observers.add( observer )
    
    # Redefine eq and hash to 
    def __eq__(self, node):
        return isinstance(node, MDNSNode) and self.node_id == node.node_id
    
    def __hash__(self):
        return  self.node_id.__hash__()
    
    def start(self):
        """On set up."""
        self.running = True
        self.browser.reset()
        if not self.initialized:
            self.udp_network.join(self)
            self.simulation.activate(self.cache, self.cache.wait_for_next_event())
            self.simulation.activate(self.responder, self.responder.answer())
        # continuous queries is the only object which needs to be restarted
        self.simulation.activate(self.browser, self.browser.query_continuously())
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
        if dns_packet.type == DNSPacket.TYPE_RESPONSE:
            # dns_packet.data is a Query object
            for record in dns_packet.data:
                self.cache.cache_record( record )
                if record.type == "TXT":
                    for observer in self.txt_observers:
                        observer.notify_txt_record(record)
        elif dns_packet.type == DNSPacket.TYPE_QUERY:
            # dns_packet.data is a List of Record objects
            self.responder.queue_query( dns_packet.data )
    
    # cache observer
    def renew_record(self, record_to_renew):
        sq = SubQuery( name = record_to_renew.name, record_type = record_to_renew.type )
        self.send_query(sq)
    
    # used by ContinuousQuerier and by self.renew_record
    def send_query(self, unique_subquery, to_node=None): # queries always through multicast
        q = Query( queries = (unique_subquery,), known_answers = self.cache.get_known_answers(), to_node=to_node )
        self.send_multicast( DNSPacket(ttype=DNSPacket.TYPE_QUERY, data=q) )
    
    # used by send_query and Responder
    def send_multicast(self, dns_packet):
        if self.running:
            self.udp_network.send_multicast(self.node_id, dns_packet)
    
    # used by Responder        
    def send_unicast(self, to_node_id, dns_packet):
        if self.running:
            self.udp_network.send_unicast(self.node_id, to_node_id, dns_packet)
    
    def write_record(self, record):
        self.responder.write_record(record)