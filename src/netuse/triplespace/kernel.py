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
from netuse.triplespace.network.server_side import CustomSimulationHandler
from netuse.triplespace.network.client_side import RequestInstance
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