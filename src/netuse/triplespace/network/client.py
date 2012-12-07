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
        simulation = request.sim
        r = ScheduledRequest(request, at=simulation.now(), simulation=simulation)
        r.start() # observers should have been added to the request itself prior to this call
        return r
    
    @staticmethod
    def launchDelayedRequest(request, wait_for):
        r = ScheduledRequest(request, delay=wait_for, simulation=request.sim)
        r.start() # observers should have been added to the request itself prior to this call
        return r
    
    @staticmethod
    def launchScheduledRequest(request, at):
        r = ScheduledRequest(request, at, simulation=request.sim)
        r.start() # observers should have been added to the request itself prior to this call
        return r
    
    @staticmethod
    def cancelRequest(request): # should be a delayed or scheduled request
        simulation = request.simulation
        pc = ProcessCanceler(request.getProcess(), sim=simulation)
        simulation.activate(pc, pc.cancel_process())


class ScheduledRequest(object):    
    def __init__(self, request, at = 'undefined', delay = 'undefined', simulation=None):
        super(ScheduledRequest, self).__init__()
        self.request = request
        self.at = at
        self.delay = delay
        self.simulation = simulation
    
    def getProcess(self):
        return self.request
    
    def start(self):
        self.simulation.activate(self.request, self.request.startup(), at=self.at, delay=self.delay)


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
        self.__url = url
        self.__data = data
        
        self.requestInit = {} # requestInit[reqId1] = now(), requestInit[reqId2] = now()
        self.responses = []
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
                
                request = HttpRequest(reqId, self.__url, data=self.__data)
                self.nodeNamesByReqId[reqId] = node.name
                
                self.requestInit[reqId] = self.sim.now()
                node.queueRequest(self, request)
                #if self.__data!=None:
                #    G.executionData.requests['data-exchanged'] += len(self.__data)
            else:
                raise Exception("A request to the same node is impossible! ")
        
        self.timer = Timer(waitUntil=G.timeout_after, sim=self.sim)
        self.timer.event.name = "request_timeout_for_%s"%(self.name)
        self.sim.activate(self.timer, self.timer.wait(), self.__maxWaitingTime)
        while not self.allReceived() or self.timer.ended:
            yield waitevent, self, (self.timer.event, self.__newResponseReceived,)
        
        
        if not self.allReceived(): # timeout reached
            #print "Response not received!"
            response_time = self.sim.now() - t_init
            
            for node_name in self.get_unanswered_nodes():
                G.traceRequest(t_init,
                           self.__actionNode.name,
                           node_name,
                           408, # TIMEOUT. See http://www.restlet.org/documentation/2.0/jse/api/org/restlet/data/Status.html#CLIENT_ERROR_REQUEST_TIMEOUT
                           response_time )
            
            # self.__actionNode.addClientRequestActivityObservation(now()-init, now())
            
            # this information can be extracted from the traces
            # G.executionData.requests['failure'].append(self)
            
        for o in self.__observers:
            o.notifyRequestFinished(self)
            
    def get_unanswered_nodes(self):
        unanswered_reqids = self.requestInit.keys()
        for response in self.responses:
            unanswered_reqids.remove(response.getid())
        
        unanswered = []
        for reqId in unanswered_reqids:
            unanswered.append(self.get_destination_node_name(reqId))
            
        return unanswered
    
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