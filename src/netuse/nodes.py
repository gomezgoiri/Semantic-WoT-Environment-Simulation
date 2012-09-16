'''
Created on Nov 26, 2011

@author: tulvur
'''
from SimPy.Simulation import *
from devices import DeviceType, RegularComputer

class NodeGenerator:
    
    def __init__(self, params):
        self.__params = params
        NodeGenerator.Nodes = {}
        self.__totalRequests = -1
    
    def generateNodes(self):
        if not self.__params.nodeTypes:
            for nodeName in self.__params.nodes:
                node = Node(nodeName)
                NodeGenerator.Nodes[nodeName] = node
                activate(node,node.processRequests())
        else:
            for nodeName, nodeType in zip(self.__params.nodes, self.__params.nodeTypes):
                node = Node(nodeName, DeviceType.create(nodeType))
                NodeGenerator.Nodes[nodeName] = node
                activate(node,node.processRequests())
    
    @staticmethod
    def getNodes():
        return NodeGenerator.Nodes.values()
    
    @staticmethod
    def getNodeByName(node_name):
        return NodeGenerator.Nodes[node_name]



class ConcurrentThread(Process):
        
    def __init__(self, node, deviceType=None, name="thread" ):
        Process.__init__(self, name=name)
        self.__node = node
        self.__device = deviceType
    
    def executeTask(self, handler, req):
        if self.__device.isOverloaded():
            self.__node.addResponse(handler.handle(req))
        else:
            yield request,self,self.__device.getResources()
            
            # do sth
            # complete the simulation with timeNeeded
            yield hold, self, self.__device.getTimeNeededToAnswer()
            
            yield release,self,self.__device.getResources()
            self.__node.addResponse(handler.handle(req))

class Node(Process):
    
    @property
    def ts(self):
        return self._ts
    
    @ts.setter
    def ts(self, ts_strategy):
        self._ts = ts_strategy
        self._ts.reasoningCapacity = self.__device.canReason
    
    @ts.deleter
    def ts(self):
        del self._ts
        
    @property
    def canReason(self):
        return self.__device.canReason
    
    
    # numThreads = number of requests per node should be specified in each Node type
    def __init__(self, name="node", device=None):
        Process.__init__(self, name=name)
        self._ts = None
        self.__device = device if device!=None else RegularComputer() # device type 
        
        self.__httpOut = {}
        self.__httpIn = []
        self.__reqIdGenerator = 0
        self.__waitingRequesters_and_InitTime = {} # TODO the "InitTime" is not longer used in this class
    
    def processRequests(self):
        while 1:
            if not self.__httpIn: # if it's empty...
                yield passivate, self
            else:
                # reqIdGenerator was not intended to be used to generate a name for CurrentThread, but I've reused :-P
                thMngr = ConcurrentThread(self, self.__device, name=self.name+"_th"+str(self.__reqIdGenerator))               
                activate(thMngr, thMngr.executeTask(self.ts.handler, self.__httpIn.pop()))
        
    def addResponse(self, response):
        self.__httpOut[response.getid()] = response
        
        requester, _ = self.__waitingRequesters_and_InitTime[response.getid()]
        del self.__waitingRequesters_and_InitTime[response.getid()]
        
        requester.addResponse(response)
    
    def queueRequest(self, requester, req):        
        self.__httpIn.append(req)
        self.__waitingRequesters_and_InitTime[req.getid()] = (requester, now())
        reactivate(self) # starts answering

        
    def __str__(self):
        return self.name