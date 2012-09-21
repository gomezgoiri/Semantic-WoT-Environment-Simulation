'''
Created on Dec 12, 2011

@author: tulvur
'''
from abc import abstractmethod, ABCMeta
from netuse.sim_utils import schedule
import urllib
from rdflib import URIRef
from rdflib.Literal import Literal

from SimPy.Simulation import now, Process, activate, hold
from netuse.results import G
from netuse.nodes import NodeGenerator
from netuse.triplespace.our_solution.whitepage.whitepage import Whitepage
from netuse.triplespace.our_solution.provider.provider import Provider
from netuse.triplespace.our_solution.consumer.consumer import Consumer
from netuse.triplespace.dataaccess.store import DataAccess
from netuse.triplespace.network.server import CustomSimulationHandler
from netuse.triplespace.network.client import RequestManager, RequestInstance, RequestObserver


class TripleSpace(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, discovery):
        self.handler = CustomSimulationHandler(self)
        self.dataaccess = DataAccess() # join not implemented yet
        self.network = None
        self.discovery = discovery
        self.__logRequests = False
        self.reasoningCapacity = False # TODO refactor (it should be get from Device
        
    @abstractmethod
    def write(self, triples):
        pass
    
    @abstractmethod
    def query(self, template):
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
    def __init__(self, discovery):
        TripleSpace.__init__(self, discovery)
    
    @schedule
    def write(self, triples):
        self.dataaccess.write(triples)
    
    @schedule
    def query(self, template):
        # local query
        
        # remote queries
        req = RequestInstance(self.discovery.me,
                              self.discovery.rest,
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(now()))
        RequestManager.launchNormalRequest(req)
        

class Centralized(TripleSpace):
    def __init__(self, me, server=None):
        TripleSpace.__init__(self, me)
        self.server = server
    
    @schedule
    def write(self, triples):
        if self.server is not None:
            req = RequestInstance(self.me, (self.server,),
                                  '/' + self.fromSpaceToURL() + "graphs/",
                                  data=triples.serialize(format='n3'),
                                  name="writeAt"+str(now()))
            RequestManager.launchNormalRequest(req)
    
    @schedule
    def query(self, template):
        req = RequestInstance(self.me, (self.server,),
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(now()))
        
        RequestManager.launchNormalRequest(req)


class OurSolution(TripleSpace, RequestObserver, Process):
    def __init__(self, discovery): # ontologyGraph, which may be already expanded or not
        Process.__init__(self)
        TripleSpace.__init__(self, discovery)
        self.provider = None
        self.consumer = None
        self.whitepage = None # just the whitepage will have this attribute to !=None
    
    @schedule
    def write(self, triples):
        self.dataaccess.write(triples)
        
        if self.provider==None:
            self.provider = Provider(self.dataaccess, self.discovery)
            activate(self.provider, self.provider.update_clues_on_whitepage())
            
        # if clues have been updated, let the provider module now
        self.provider.refresh_clue()
    
    @schedule
    def query(self, template):        
        if self.consumer==None:
            self.consumer = Consumer(self.discovery) # change the discovery registry to set "sac" property
        
        
        
        # remote queries
        activate(self, self._finish_query_waiting(template)) # to wait for whitepages
    
    def _finish_query_waiting(self, template):
        # local query
        
        
        selected_nodes = None
        while selected_nodes==None:
            try:
                selected_nodes = self.consumer.get_query_candidates(template)
            except Exception:
                #print "Waiting for a whitepage."
                pass
            yield hold, self, 100
        
        destNodes = []
        for node_name in selected_nodes:
            if node_name is not self.discovery.me.name: # local query already done
                destNodes.append(NodeGenerator.getNodeByName(node_name))
        
        req = RequestInstance(self.discovery.me, destNodes,
                              '/' + self.fromSpaceToURL() + "query/" + self.fromTemplateToURL(template),
                              name="queryAt"+str(now()))
        RequestManager.launchNormalRequest(req)
    
    def be_whitepage(self):
        self.whitepage = Whitepage()
        self.discovery.me.discovery_record.is_whitepage=True
        # TODO check if another whitepage already exist and resolve conflict (step 6)
    
    def notifyRequestFinished(self, request_instance):
        pass # do I really need the results?