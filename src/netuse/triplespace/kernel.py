'''
Created on Dec 12, 2011

@author: tulvur
'''
from abc import abstractmethod, ABCMeta
from netuse.sim_utils import schedule
from SimPy.Simulation import now, Process, activate, hold

from netuse.nodes import NodeGenerator
from netuse.triplespace.our_solution.whitepage.whitepage import Whitepage
from netuse.triplespace.our_solution.provider.provider import Provider
from netuse.triplespace.our_solution.consumer.consumer import ConsumerFactory
from netuse.triplespace.dataaccess.store import DataAccess
from netuse.triplespace.network.url_utils import URLUtils
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
                              '/' + self.serialize_space_to_URL() + "query/" + URLUtils.serialize_wildcard_to_URL(template),
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
                                  '/' + self.serialize_space_to_URL() + "graphs/",
                                  data=triples.serialize(format='n3'),
                                  name="writeAt"+str(now()))
            RequestManager.launchNormalRequest(req)
    
    @schedule
    def query(self, template):
        req = RequestInstance(self.me, (self.server,),
                              '/' + self.serialize_space_to_URL() + "query/" + URLUtils.serialize_wildcard_to_URL(template),
                              name="queryAt"+str(now()))
        
        RequestManager.launchNormalRequest(req)


class OurSolution(TripleSpace):
    def __init__(self, discovery): # ontologyGraph, which may be already expanded or not
        TripleSpace.__init__(self, discovery)
        self.provider = None
        self.consumer = None
        self.whitepage = None # just the whitepage will have this attribute to !=None
        
    def be_whitepage(self):
        self.whitepage = Whitepage()
        self.discovery.me.discovery_record.is_whitepage=True
        # TODO check if another whitepage already exist and resolve conflict (step 6)
    
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
            self.consumer = ConsumerFactory.createConsumerFor(self.discovery) # change the discovery registry to set "sac" property
        
        # remote queries
        qf = QueryFinisher(self.consumer, self.discovery, self.serialize_space_to_URL(), URLUtils.serialize_wildcard_to_URL(template))
        # when I've tried to do it in the same class (qf = self), some of the activation weren't really activated
        # may be because a method of the same object cannot be used at the same simulation time?
        # In this case, when they overlap, the activation of _finish_query_waiting may be ignored when they overlap in time
        activate(qf, qf._finish_query_waiting(template)) # to wait for whitepages

class QueryFinisher(Process, RequestObserver):
    
    def __init__(self, consumer, discovery, fromSpaceToURL, fromTemplateToURLtemplate):
        Process.__init__(self)
        self.consumer = consumer
        self.discovery = discovery
        self.fromSpaceToURL = fromSpaceToURL
        self.fromTemplateToURLtemplate = fromTemplateToURLtemplate
    
    def _finish_query_waiting(self, template):
        # local query
        
        selected_nodes = None
        previously_unsolved = True
        attempts = 5 # to avoid too many process on memory when no clue has been checked
        while selected_nodes==None and attempts>0:
            try:
                selected_nodes = self.consumer.get_query_candidates(template, previously_unsolved)
                previously_unsolved = False
            except Exception as e:
                #print "Waiting for a whitepage.", e.args[0]
                attempts -= 1
            yield hold, self, 100
            
        if attempts==0:
            # somehow record this failure
            print "No clues have been initialized"
            pass
        else:
            try:
                if len(selected_nodes)>0:
                    destNodes = []
                    for node_name in selected_nodes:
                        if node_name!=self.discovery.me.name: # local query already done
                            destNodes.append(NodeGenerator.getNodeByName(node_name))
                    
                    req = RequestInstance(self.discovery.me, destNodes,
                                          '/' + self.fromSpaceToURL + "query/" + self.fromTemplateToURLtemplate,
                                          name="queryAt"+str(now()))
                    RequestManager.launchNormalRequest(req)
            except:
                import traceback
                traceback.print_exc()
                raise
    
    def notifyRequestFinished(self, request_instance):
        pass # do I really need the results?