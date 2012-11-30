'''
Created on Nov 26, 2011

@author: tulvur
'''
from SimPy.Simulation import Process, activate, passivate, reactivate, hold, release, request, now
import weakref
from devices import DeviceType, RegularComputer
from netuse.triplespace.network.discovery import DiscoveryRecord

class NodeGenerator:
    
    def __init__(self, params, simulation=None):
        self.__params = params
        self.__simulation = simulation
        NodeGenerator.Nodes = {}
        self.__totalRequests = -1
    
    def generateNodes(self):
        for nodeName, nodeType in zip(self.__params.nodes, self.__params.nodeTypes):
            node = Node(nodeName, DeviceType.create(nodeType), sim=self.__simulation)
            NodeGenerator.Nodes[nodeName] = node
            activate(node,node.processRequests())
    
    @staticmethod
    def getNodes():
        return NodeGenerator.Nodes.values()
    
    @staticmethod
    def getNodeByName(node_name):
        return NodeGenerator.Nodes[node_name]


class ConcurrentThread(Process):
        
    def __init__(self, node, deviceType=None, name="thread", sim=None):
        Process.__init__(self, name=name, sim=sim)
        self.__node = weakref.proxy(node)
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
    
    def __init__(self, name="node", device=None, joined_since=1, sac=False, battery_lifetime=1, sim=None):
        Process.__init__(self, name=name, sim=sim)
        self._ts = None
        self.__device = device if device!=None else RegularComputer() # device type 
        
        self.discovery_record = DiscoveryRecord(memory = device.ram_memory,
                                                storage = device.storage_capacity,
                                                joined_since = joined_since,
                                                sac = sac,
                                                battery_lifetime = battery_lifetime if device.hasBattery else DiscoveryRecord.INFINITE_BATTERY)
        
        self.__httpIn = []
        self.__reqIdGenerator = 0
        self.__waitingRequesters_and_InitTime = {} # TODO the "InitTime" is not longer used in this class
    
    def processRequests(self):
        while 1:
            if not self.__httpIn: # if it's empty...
                yield passivate, self
            else:
                # reqIdGenerator was not intended to be used to generate a name for CurrentThread, but I've reused :-P
                thMngr = ConcurrentThread(self, self.__device, name=self.name+"_th"+str(self.__reqIdGenerator), sim=self.sim)
                activate(thMngr, thMngr.executeTask(self.ts.handler, self.__httpIn.pop()))
        
    def addResponse(self, response):        
        requester, _ = self.__waitingRequesters_and_InitTime[response.getid()]
        del self.__waitingRequesters_and_InitTime[response.getid()]
        
        requester.addResponse(response)
    
    def queueRequest(self, requester, req):        
        self.__httpIn.append(req)
        self.__waitingRequesters_and_InitTime[req.getid()] = (requester, now())
        reactivate(self) # starts answering

    def stop(self):
        self._ts.stop()
    
    def __str__(self):
        return self.name