'''
Created on Nov 26, 2011

@author: tulvur
'''
from SimPy.Simulation import Process, Resource, passivate, hold, release, request
import weakref
from devices import DeviceType, RegularComputer
from netuse.triplespace.network.discovery import DiscoveryRecord

class NodeGenerator(object):
    
    def __init__(self, params, simulation=None):
        self.__params = params
        self.__simulation = simulation
        NodeGenerator.Nodes = {}
        self.__totalRequests = -1
    
    def generateNodes(self):
        for nodeName, nodeType in zip(self.__params.nodes, self.__params.nodeTypes):
            node = Node(nodeName, DeviceType.create(nodeType), sim=self.__simulation)
            NodeGenerator.Nodes[nodeName] = node
            self.__simulation.activate(node,node.processRequests())
    
    @staticmethod
    def getNodes():
        return NodeGenerator.Nodes.values()
    
    @staticmethod
    def getNodeByName(node_name):
        return NodeGenerator.Nodes[node_name]


class ConcurrentThread(Process):
        
    def __init__(self, node, device, connections, sim, name="thread"):
        super(ConcurrentThread, self).__init__(name=name, sim=sim)
        self.__node = weakref.proxy(node)
        self.__device = device
        self.__connections = connections
    
    def executeTask(self, handler, req):
        if self.__connections.is_overloaded():
            self.__node.addResponse(handler.handle(req))
        else:
            yield request, self, self.__connections
            
            # do sth
            # complete the simulation with timeNeeded
            yield hold, self, self.__device.get_time_needed_to_answer( self.__connections.get_current_requests() )
            
            yield release, self, self.__connections
            self.__node.addResponse(handler.handle(req))


class Connections(Resource):
    
    def __init__(self, device, sim, name="connections"):
        super(Connections, self).__init__( device.get_maximum_concurrent_requests() ,
                                           name=name,
                                           sim=sim )
        self.canQueue = device.canQueue
    
    def get_current_requests(self):
        return self.capacity - self.n
    
    def is_overloaded(self):
        return not self.canQueue and self.n<=0


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
        super(Node, self).__init__(name=name, sim=sim)
        self._ts = None
        self.__device = device if device!=None else RegularComputer() # device type 
        self.__connections = Connections( self.__device, sim = sim, name = "%s's connections"%(name) )
        
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
                thMngr = ConcurrentThread( self,
                                           self.__device,
                                           self.__connections,
                                           name = "%s_th%d"%(self.name, self.__reqIdGenerator),
                                           sim = self.sim)
                self.sim.activate(thMngr, thMngr.executeTask(self.ts.handler, self.__httpIn.pop()))
        
    def addResponse(self, response):        
        requester, _ = self.__waitingRequesters_and_InitTime[response.getid()]
        del self.__waitingRequesters_and_InitTime[response.getid()]
        
        requester.addResponse(response)
    
    def queueRequest(self, requester, req):        
        self.__httpIn.append(req)
        self.__waitingRequesters_and_InitTime[req.getid()] = (requester, self.sim.now())
        self.sim.reactivate(self) # starts answering

    def stop(self):
        self._ts.stop()
    
    def __str__(self):
        return self.name