'''
Created on Dec 12, 2011

@author: tulvur
'''
import urllib
from abc import abstractmethod, ABCMeta
from rdflib import URIRef
from rdflib.Literal import Literal

from SimPy.Simulation import *
from netuse.triplespace.dataaccess.store import DataAccess
from netuse.triplespace.network.httpelements import HttpRequest
from netuse.triplespace.network.handlers import CustomSimulationHandler
from netuse.results import G
from netuse.triplespace.gossiping.gossiping_mechanism import GossipingBase
from netuse.nodes import NodeGenerator

class TripleSpace(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, me):
        self.handler = CustomSimulationHandler(self)
        self.dataaccess = DataAccess() # join not implemented yet
        self.network = None
        self.me = me
        self.__logRequests = False
        self.reasoningCapacity = False # TODO refactor (it should be get from Device
    
    def setLogRequests(self, logRequests):
        if not self.__logRequests:
            if logRequests: self.requests = []
        self.__logRequests = logRequests
    
    def logRequest(self, req):
        if self.__logRequests: self.requests.append(req)
        
    @abstractmethod
    def write(self, startAt=now()):
        pass
    
    @abstractmethod
    def query(self, template, startAt=now()):
        pass
    
    def fromTemplateToURL(self, template):
        s = template[0]
        p = template[1]
        o = template[2]
        
        ret = 'wildcards/'
        
        ret += urllib.quote_plus(s) if s!=None else '*'
        ret += '/'
        ret += urllib.quote_plus(p) if p!=None else '*'
        ret += '/'
        
        if o is None:
            ret += '*/'
        elif isinstance(o, URIRef):
            ret += urllib.quote_plus(o)
            ret += '/'
        elif isinstance(o, Literal):
            ret += urllib.quote_plus(o.datatype)
            ret += '/'
            ret += urllib.quote(o) # or o.toPython()
            ret += '/'
            
        return ret
    
    def fromSpaceToURL(self, space=G.defaultSpace):
        return 'spaces/' + urllib.quote_plus(space) + '/'

class NegativeBroadcasting(TripleSpace):
    def __init__(self, me):
        TripleSpace.__init__(self, me)
    
    def write(self, triples, startAt=now()):
        self.dataaccess.write(triples)
    
    def query(self, template, startAt=now()):
        # local query
        
        # remote queries
        req = RequestInstance(self.me, self.destNodes,
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(startAt))
        activate(req, req.startup(), at=startAt)
        self.logRequest(req)
    
    def setNodes(self, listNodes):
        self.destNodes = list(listNodes)
        self.destNodes.remove(self.me) # just in case
        

class Centralized(TripleSpace):
    def __init__(self, me, server=None):
        TripleSpace.__init__(self, me)
        self.server = server
    
    def write(self, triples, startAt=now()):
        if self.server is not None:
            req = RequestInstance(self.me, (self.server,),
                                  '/' + self.fromSpaceToURL() + "graphs/",
                                  data=triples.serialize(format='n3'), name="writeAt"+str(startAt))
            activate(req, req.startup(), at=startAt)
            self.logRequest(req)
    
    def query(self, template, startAt=now()):
        req = RequestInstance(self.me, (self.server,),
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(startAt))
        activate(req, req.startup(), at=startAt)
        self.logRequest(req)


class Gossiping(NegativeBroadcasting):
    def __init__(self, me, ontologyGraph): # ontologyGraph, which may be already expanded or not
        NegativeBroadcasting.__init__(self, me)
        self.gossiping_base = GossipingBase(ontologyGraph)
        self.templateToQueryAfterGossiping = {}
    
    def write(self, triples, startAt=now()):
        self.dataaccess.write(triples)
    
    def query(self, template, startAt=now()):
        qs = GossipingQueryStarter(template, self)
        activate(qs, qs.startup(), at=startAt)
        
    def _continue_query(self, template):
        # local query
        
        # remote queries
        ungossiped_nodes = self.gossiping_base.getUngossiped(self.destNodes)
        if ungossiped_nodes:
            req = RequestInstance(self.me, ungossiped_nodes,
                                  '/' + self.fromSpaceToURL() + "gossip/",
                                  name="gossipAt"+str(now()))
            
            self.addObserver(req, template)
            activate(req, req.startup(), at=now())
        else:
            self.perform_query(template, now())
    
    def addObserver(self, requestInstance, template): # queue pending query
        self.templateToQueryAfterGossiping[requestInstance] = template
        requestInstance.addObserver(self)
    
    def notifyRequestFinished(self, requestInstance):
        # store gossips
        for response in requestInstance.responses:
            if response.getstatus()==200:
                dest_node_name = requestInstance.extractDestinationNode(response.getid())
                self.gossiping_base.addGossip(dest_node_name, response.get_data(), expand=False) #TODO put it again self.reasoningCapacity)
        
        # extract template for pending query
        template = self.templateToQueryAfterGossiping[requestInstance]
        del self.templateToQueryAfterGossiping[requestInstance]
        
        # now we can perform the query
        self.perform_query(template, startAt=now())
    
    def perform_query(self, template, startAt):
        selected_nodes = self.gossiping_base.getQueriableNodes(template)
        destNodes = []
        for node_name in selected_nodes:
            destNodes.append(NodeGenerator.getNodeByName(node_name))
        
        req = RequestInstance(self.me, destNodes,
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(startAt))
        activate(req, req.startup(), at=startAt)
        self.logRequest(req)

class GossipingQueryStarter(Process):
    """ This class performs a delayed query in a Gossiping kernel """    
    
    def __init__(self, template, kernel):
        Process.__init__(self)
        self.template = template
        self.kernel = kernel
        
    def startup(self):
        self.kernel._continue_query(self.template)
        yield hold, self, 1 # to make the process possible

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