'''
Created on Sep 16, 2012

@author: tulvur
'''

class DiscoveryFactory(object):
    
    def __init__(self, nodes):
        self.nodes = nodes
        
    def create_simple_discovery(self, localNode):
        restOfTheNodes = list(self.nodes)
        restOfTheNodes.remove(localNode) # substract localNode from the original list and create
        return SimpleDiscoveryMechanism(localNode, restOfTheNodes)
        

class SimpleDiscoveryMechanism(object):
    def __init__(self, me, rest):
        self.me = me
        self.rest = rest

    def get_consumers(self):
        pass