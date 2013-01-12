'''
Created on Jan 12, 2013

@author: tulvur
'''

from netuse.triplespace.network.discovery.mdns.cache import Cache

class Responder(object):
    
    def __init__(self):
        self.cache = Cache()
    
    def start(self):
        """On set up."""
        pass
    
    def stop(self):
        """Call when it goes down for whatever reason."""
        pass