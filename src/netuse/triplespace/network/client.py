'''
Created on Sep 10, 2012

@author: tulvur
'''

from SimPy.Simulation import *
from netuse.triplespace.network.httpelements import HttpRequest
from netuse.results import G


class RequestInstance(Process):
    """ This class performs an HTTP request in SimPy """
    
    ReqIdGenerator = 0
    
    def __init__(self, actionNode, destinationNodes, url, data=None, waitUntil=10000.0, name="request"):
        Process.__init__(self, name=name)
        self.__actionNode = actionNode
        self.__destinationNodes = destinationNodes # tuple with all the nodes to be requested
        self.__url = url
        self.__data = data
        
        self.requestInit = {} # requestInit[reqId1] = now(), requestInit[reqId2] = now()
        self.responses = []
        self.__maxWaitingTime = waitUntil
        self.nodeNamesByReqId = {} # used in the gossiping mechanism with the gossiping requests
        
        self.__timeout = SimEvent()
        self.__newResponseReceived = SimEvent()
        self.__observers = []
        
    def startup(self):
        init = now()
        
        for node in self.__destinationNodes:
            # already removed from the list prior to calling to this method, but just in case...
            if node is not self.__actionNode:
                reqId = RequestInstance.ReqIdGenerator
                RequestInstance.ReqIdGenerator += 1
                
                request = HttpRequest(reqId, self.__url, data=self.__data)
                self.nodeNamesByReqId[reqId] = node.name
                
                self.requestInit[reqId] = now()
                node.queueRequest(self, request)
                if self.__data!=None:
                    G.executionData.requests['data-exchanged'] += len(self.__data)
            else:
                raise Exception("A request to the same node is impossible!")
        
        self.timer = Timer(self.__timeout, waitUntil=G.timeout_after)
        activate(self.timer, self.timer.wait(), self.__maxWaitingTime)
        while not self.allReceived() or self.timer.ended:
            yield waitevent, self, (self.__timeout, self.__newResponseReceived,)
        
        if self.allReceived():
            #print "All the responses get by node %s: %s"%(self.__actionNode,self.responses)
            self.__actionNode.addClientRequestActivityObservation(now()-init, now())
            G.executionData.requests['success'].append(self)
        else: # timeout reached
            #print "Response not received!"
            self.__actionNode.addClientRequestActivityObservation(now()-init, now())
            G.executionData.requests['failure'].append(self)
            G.executionData.requests['timeout'].append(self.getWaitingFor())
            
        for o in self.__observers:
            o.notifyRequestFinished(self)
    
    def allReceived(self):
        return self.getWaitingFor()==0
    
    def getWaitingFor(self):
        return len(self.requestInit)
    
    def addResponse(self, response): # TODO associate with a node
        #if response.getstatus()==404:
        #    dest_node_name = self.extractDestinationNode(response.getid())
        #    print dest_node_name
        
        # timeouts have been already taken into account in the 'timeout' counter
        if not self.timer.ended:
            t_init = self.requestInit[response.getid()]
            G.executionData.response_time_monitor.observe( now() - t_init ) # request time
            del self.requestInit[response.getid()]
            
            self.responses.append(response) #dest_node_name
            G.executionData.requests['data-exchanged'] += len(response.get_data())
            
            #fileHandle = open ( 'test.txt', 'a' )
            #fileHandle.write ( response.get_data() )
            #fileHandle.close()
            
            self.__newResponseReceived.signal()
            
    def extractDestinationNode(self, responseId):
        ret = self.nodeNamesByReqId[responseId]
        del self.nodeNamesByReqId[responseId]
        return ret
         
    def rejectConnection(self, requestId):
        # timeouts have been already taken into account in the 'timeout' counter
        if not self.timer.ended:
            del self.requestInit[requestId]
            G.executionData.requests['server-error'] += 1
            self.__newResponseReceived.signal()
    
    def toString(self):
        for resp in self.responses:
            print resp.getmsg()
    
    def getActionNode(self):
        return self.__actionNode
    
    def addObserver(self, observer):
        self.__observers.append(observer)


class Timer(Process):
    def __init__(self, event, waitUntil=10000.0, name="timer"):
        Process.__init__(self, name=name)
        self.__timeout = waitUntil
        self.__event = event
        self.ended = False
        
    def wait(self):
        yield hold, self, self.__timeout
        self.ended = True
        self.__event.signal()