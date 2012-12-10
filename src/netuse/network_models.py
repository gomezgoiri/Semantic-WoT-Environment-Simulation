'''
Created on Dec 8, 2012

@author: tulvur
'''

class NetworkModelManager(object):
    """
    Class which runs different network models which simulate activity from nodes leaving and joining the network.
    """
    
    @staticmethod
    def run_model(model="normal"):
        if model==DynamicNodesModel.ID:
            pass
        elif model==ChaoticModel.ID:
            pass
        else: # model=="normal" or None or invalid
            pass # do nothing


class DynamicNodesModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    ID = "dynamic"
    
    pass

class ChaoticModel(object):
    """
    A Model where the nodes go down and up periodically.
    """
    
    ID = "chaotic"
    
    pass