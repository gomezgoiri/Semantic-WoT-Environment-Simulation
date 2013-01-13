'''
Created on Jan 12, 2013

@author: tulvur
'''

from netuse.mdns.cache import Cache
from netuse.mdns.responder import Responder

class MDNSNetwork(object):
    
    def __init__(self):
        self.mdns_nodes = []    
    
    def join(self, node):
        self.mdns_nodes.append(node)
    
    def send_multicast(self, dns_packet):
        for mdns_node in self.mdns_nodes:
            pass
            
    def send_unicast(self, node_id):
        pass
            
    

class MDNSNode(object):
    
    def __init__(self, sim):
        self.responder = Responder(sim)
        self.cache = Cache(sim)
    
    def start(self):
        """On set up."""
        pass
    
    def stop(self):
        """Call when it goes down for whatever reason."""
        self.cache.flush_all()