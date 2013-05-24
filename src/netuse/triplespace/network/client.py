'''
Created on Sep 10, 2012

@author: tulvur
'''

from SimPy.Simulation import Process, SimEvent, hold, waitevent
import weakref
from abc import ABCMeta, abstractmethod
from netuse.sim_utils import Timer
from netuse.triplespace.network.httpelements import HttpRequest
from netuse.results import G


class ProcessCanceler(Process):
    def __init__(self, victimProcess, sim=None):
        super(ProcessCanceler, self).__init__(sim=sim, name="Canceler")
        self.victimProcess = victimProcess
        
    def cancel_process(self):
        yield hold, self, 0 # the activator function of a Process should be a generator (contain a yield)
        self.cancel(self.victimProcess) # cancel is Process object's method, that's why we need to create this class


class RequestManager(object):
    
    @staticmethod
    def launchNormalRequest(request):
        request.sim.activate(request, request.startup())
    
    @staticmethod
    def launchDelayedRequest(request, wait_for):
        request.sim.activate(request, request.startup(), delay=wait_for)
    
    @staticmethod
    def launchScheduledRequest(request, at):
        request.sim.activate(request, request.startup(), at=at)
    
    @staticmethod
    def cancelRequest(request):
        simulation = request.sim
        pc = ProcessCanceler(request, sim=simulation)
        simulation.activate(pc, pc.cancel_process())


class RequestObserver(object):    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def notifyRequestFinished(self, request_instance):
        pass


class RequestInstance(Process): # TODO rename to something more meaningful such as RequestSender
    """ This class performs an HTTP request in SimPy """
    
    ReqIdGenerator = 0
    
    def __init__(self, actionNode, destinationNodes, url, data=None, waitUntil=10000.0, name="request", sim=None):
        super(RequestInstance, self).__init__(name=name, sim=sim)
        self.name += " (from=%s, url=%s)"%(actionNode.name, url)
        self.__actionNode = weakref.proxy(actionNode) #weakref.ref(actionNode)
        self.__destinationNodes = weakref.WeakSet(destinationNodes) # tuple with all the nodes to be requested
        self.url = url # accessible
        self.__data = data
        
        self.requestInit = {} # requestInit[reqId1] = now(), requestInit[reqId2] = now()
        self.responses = [] # accessible
        self.__maxWaitingTime = waitUntil
        self.nodeNamesByReqId = {} # used in the gossiping mechanism with the gossiping requests
        
        self.__newResponseReceived = SimEvent(name="request_response_for_%s"%(self.name), sim=sim)
        self.__observers = weakref.WeakSet()
    
        
    def startup(self):
        t_init = self.sim.now()
        
        for node in self.__destinationNodes:
            # already removed from the list prior to calling to this method, but just in case...
            if node is not self.__actionNode:
                reqId = RequestInstance.ReqIdGenerator
                RequestInstance.ReqIdGenerator += 1
                
                request = HttpRequest(reqId, self.url, data=self.__data)
                self.nodeNamesByReqId[reqId] = node.name
                
                self.requestInit[reqId] = self.sim.now()
                node.queueRequest(self, request)
                #if self.__data!=None:
                #    G.executionData.requests['data-exchanged'] += len(self.__data)
            else:
                raise Exception("A request to the same node is impossible! ")
        
        self.timer = Timer(waitUntil=G.timeout_after, sim=self.sim)
        self.timer.event.name = "request_timeout_for_%s"%(self.name)
        self.sim.activate(self.timer, self.timer.wait())#, self.__maxWaitingTime)
        while not self.allReceived() and not self.timer.ended:
            yield waitevent, self, (self.timer.event, self.__newResponseReceived,)
        
        
        if not self.allReceived(): # timeout reached
            #print "Response not received!"
            response_time = self.sim.now() - t_init
            
            for node_name in self.get_unanswered_nodes():
                G.traceRequest(t_init,
                           self.__actionNode.name,
                           node_name,
                           self.url,
                           408, # TIMEOUT. See http://www.restlet.org/documentation/2.0/jse/api/org/restlet/data/Status.html#CLIENT_ERROR_REQUEST_TIMEOUT
                           response_time )
            
            # self.__actionNode.addClientRequestActivityObservation(now()-init, now())
            
            # this information can be extracted from the traces
            # G.executionData.requests['failure'].append(self)
            
        for o in self.__observers:
            o.notifyRequestFinished(self)
            
    def get_unanswered_nodes(self):
        # not yet deleted requestInit keys, are the ids without a response
        return [self.get_destination_node_name(reqId) for reqId in self.requestInit.keys()]
    
    def getWaitingFor(self):
        return len(self.requestInit)
    
    def allReceived(self):
        return self.getWaitingFor()==0
    
    def addResponse(self, response): # TODO associate with a node
        #if response.getstatus()==404:
        #    dest_node_name = self.get_destination_node_name(response.getid())
        #    print dest_node_name
        
        # timeouts have been already taken into account in the 'timeout' counter
        if not self.timer.ended:
            t_init = self.requestInit[response.getid()]
            response_time = self.sim.now() - t_init
            G.traceRequest(t_init,
                           self.__actionNode.name,
                           self.get_destination_node_name(response.getid()),
                           response.geturl(),
                           response.getstatus(),
                           response_time )
            
            #G.executionData.response_time_monitor.observe( now() - t_init ) # request time
            del self.requestInit[response.getid()]
            
            self.responses.append(response) #dest_node_name
            
            #G.executionData.requests['data-exchanged'] += len(response.get_data())
            
            #fileHandle = open ( 'test.txt', 'a' )
            #fileHandle.write ( response.get_data() )
            #fileHandle.close()
            
            self.__newResponseReceived.signal()
            
    def get_destination_node_name(self, responseId):
        return self.nodeNamesByReqId[responseId]
    
    def toString(self):
        for resp in self.responses:
            print resp.getmsg()
    
    def getActionNode(self):
        return self.__actionNode
    
    def addObserver(self, observer):
        self.__observers.add(observer)