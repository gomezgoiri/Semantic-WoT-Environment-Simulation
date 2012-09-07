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
    
    def getTotalRequests(self):
        if self.__totalRequests==-1 :
            self.__totalRequests = 0
            for n in NodeGenerator.getNodes():
                self.__totalRequests += n.getReceivedRequests()  
        return self.__totalRequests
    
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
            self.__node.rejectRequest(req.getid())
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
        
        self.__inactivityMonitor = Monitor()
        # to monitor the time needed by the node as request client
        self.__requestActivityMonitor = Monitor()
        self.__requestsCounter = 0
    
    def processRequests(self):
        while 1:
            if not self.__httpIn: # if it's empty...
                inactive = now()
                yield passivate, self
                self.__inactivityMonitor.observe(now()-inactive)
            else:
                # reqIdGenerator was not intended to be used to generate a name for CurrentThread, but I've reused :-P
                thMngr = ConcurrentThread(self, self.__device, name=self.name+"_th"+str(self.__reqIdGenerator))               
                activate(thMngr, thMngr.executeTask(self.ts.handler, self.__httpIn.pop()))
    
    def getInactivityPeriod(self):
        return self.__inactivityMonitor.total()
    
    def addResponse(self, response):
        self.__httpOut[response.getid()] = response
        
        requester, _ = self.__waitingRequesters_and_InitTime[response.getid()]
        del self.__waitingRequesters_and_InitTime[response.getid()]
        
        #G.executionData.response_time_monitor.observe(now()-t_init)
        requester.addResponse(response)
    
    def rejectRequest(self, requestId):        
        requester, _ = self.__waitingRequesters_and_InitTime[requestId]
        del self.__waitingRequesters_and_InitTime[requestId]
        
        requester.rejectConnection(requestId) # implement this method!
    
    def queueRequest(self, requester, req):
        self.__requestsCounter += 1
        
        self.__httpIn.append(req)
        self.__waitingRequesters_and_InitTime[req.getid()] = (requester, now())
        reactivate(self) # starts answering
        
    def addClientRequestActivityObservation(self, y, t=now()):
        self.__requestActivityMonitor.observe(y, t)
        
    def getInactivityMonitor(self):
        return self.__inactivityMonitor
    
    def getActivityMonitor(self):
        return self.__requestActivityMonitor
    
    def getReceivedRequests(self):
        return self.__requestsCounter
        
    def __str__(self):
        return self.name