'''
Created on Jan 12, 2013

@author: tulvur
'''

from netuse.triplespace.network.discovery.mdns.responder import Responder

class MDNSNetwork(object):
    
    def __init__(self):
        self.mdns_nodes = []    
    
    def join(self, node):
        self.mdns_nodes.append(node)
    
    def send_multicast(self, msg):
        for mdns_node in self.mdns_nodes:
            
    

class MDNSNode(object):
    
    def __init__(self):
        self.responder = Responder()
        