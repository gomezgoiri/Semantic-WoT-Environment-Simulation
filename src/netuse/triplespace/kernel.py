# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import json
from abc import abstractmethod, ABCMeta
from netuse.sim_utils import schedule
from SimPy.Simulation import Process, hold
from clueseval.clues.storage.abstract_store import AggregationClueUtils # to manually parse the json
from clueseval.clues.versions.management import Version
from netuse.nodes import NodeManager
from netuse.triplespace.caching.queries import QueryCacher 
from netuse.triplespace.our_solution.whitepage.whitepage import Whitepage
from netuse.triplespace.our_solution.provider.provider import Provider
from netuse.triplespace.our_solution.consumer.consumer import ConsumerFactory
from netuse.triplespace.dataaccess.store import DataAccess
from netuse.triplespace.network.url_utils import URLUtils
from netuse.triplespace.network.client import RequestManager, RequestInstance, RequestObserver


class TripleSpace(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.discovery = None # should be set
        
        self.__logRequests = False
        self.reasoningCapacity = False # TODO refactor (it should be get from Device
        
        self.dataaccess = DataAccess() # join not implemented yet
        self.network = None
    
    
    @abstractmethod
    def write(self, triples):
        pass
    
    @abstractmethod
    def query(self, template):
        pass

    def stop(self):
        pass
    
    # used to reset some settings before joining the network again
    def recover_from_drop(self):
        pass


class NegativeBroadcasting(TripleSpace):
    def __init__(self, simulation):
        super(NegativeBroadcasting, self).__init__(simulation)
    
    @schedule
    def write(self, triples):
        self.dataaccess.write(triples)
    
    @schedule
    def query(self, template):
        # local query
        
        # remote queries
        req = RequestInstance(self.discovery.me,
                              self.discovery.get_nodes(),
                              '/' + URLUtils.serialize_space_to_URL() + "query/" + URLUtils.serialize_wildcard_to_URL(template),
                              name = "queryAt"+str(self.simulation.now()),
                              sim = self.simulation )
        RequestManager.launchNormalRequest(req)


class NegativeBroadcastingCaching(NegativeBroadcasting, RequestObserver):
    def __init__(self, simulation):
        super(NegativeBroadcastingCaching, self).__init__(simulation)
        self.cache = QueryCacher()
        self.url_beginning = '/' + URLUtils.serialize_space_to_URL() + "query/"
    
    @schedule
    def write(self, triples):
        self.dataaccess.write(triples)
    
    @schedule
    def query(self, template):
        # local query
        
        # remote queries
        relevants = self.cache.get_relevant_nodes( template, self.discovery.get_nodes() )
        req = RequestInstance(self.discovery.me,
                              relevants,
                              self.url_beginning + URLUtils.serialize_wildcard_to_URL(template),
                              name = "queryAt"+str(self.simulation.now()),
                              sim = self.simulation )
        req.addObserver(self)
        RequestManager.launchNormalRequest(req)
    
    def notifyRequestFinished(self, request_instance):
        template = URLUtils.parse_wildcard_url( request_instance.url[ len(self.url_beginning): ] )
        for response in request_instance.responses:
            self.cache.cache(template, request_instance.get_destination_node_name(response.getid()), response) # do I really need the results?


class Centralized(TripleSpace):
    def __init__(self, me, server, simulation):
        super(Centralized, self).__init__(simulation, None)
        self.server = server
    
    @schedule
    def write(self, triples):
        if self.server is not None:
            req = RequestInstance(self.me, (self.server,),
                                  '/' + URLUtils.serialize_space_to_URL() + "graphs/",
                                  data = triples.serialize(format='n3'),
                                  name = "writeAt"+str(self.simulation.now()),
                                  sim = self.simulation )
            RequestManager.launchNormalRequest(req)
    
    @schedule
    def query(self, template):
        req = RequestInstance(self.me, (self.server,),
                              '/' + URLUtils.serialize_space_to_URL() + "query/" + URLUtils.serialize_wildcard_to_URL(template),
                              name = "queryAt"+str(self.simulation.now()),
                              sim = self.simulation )
        
        RequestManager.launchNormalRequest(req)


class OurSolution(TripleSpace):
    def __init__(self, simulation): # ontologyGraph, which may be already expanded or not
        super(OurSolution, self).__init__(simulation)
        self.provider = None
        self.consumer = None
        self.whitepage = None # just the whitepage will have this attribute to !=None
    
    def be_whitepage(self, json_clues_sent_by_the_chooser):
        my_clue_store = None if self.consumer is None else self.consumer.get_clue_store()
        
        # In some cases, we could reuse the clue store used by the "Consumer" module.
        # However, in order to simplify the synchronization between the 2 modules
        # data from the consumer's clue store is loaded into a different
        # clue store managed by the WP. 
        self.whitepage = Whitepage( generation_time = self.simulation.now() )
        
        if my_clue_store is None:
                if json_clues_sent_by_the_chooser is not None:
                    self.whitepage.initial_data_loading( json_clues_sent_by_the_chooser )
        else: # if the sent clues are newer load them, otherwise don't
            if json_clues_sent_by_the_chooser is None:
                consumers_data_json = my_clue_store.toJson()
                self.whitepage.initial_data_loading( consumers_data_json )
            else:
                dictio = json.loads(json_clues_sent_by_the_chooser)
                sent_version = Version( dictio[AggregationClueUtils.GENERATION_FIELD],
                                        dictio[AggregationClueUtils.VERSION_FIELD] )
                
                if sent_version < my_clue_store.version:
                    consumers_data_json = my_clue_store.toJson()
                    self.whitepage.initial_data_loading( consumers_data_json )
                else:
                    self.whitepage.initial_data_loading( json_clues_sent_by_the_chooser )
        
        # A WP shares through discovery record the first version it started providing
        self.discovery.get_my_record().change_transactionally( is_whitepage = True,
                                                               version = self.whitepage.get_initially_loaded_version() )
        
        # TODO check if another whitepage already exist and resolve conflict (step 6)
    
    @schedule
    def write(self, triples):
        self.dataaccess.write(triples)
        
        if self.provider is None:
            self.provider = Provider( self.dataaccess, self.discovery, sim = self.simulation )
            self.simulation.activate( self.provider, self.provider.update_clues_on_whitepage() )
            
        # if clues have been updated, let the provider module now
        self.provider.refresh_clue()
    
    @schedule
    def query(self, template):
        if self.consumer is None:
            factory = ConsumerFactory(self.simulation, self.discovery)
            self.consumer = factory.createConsumer()
        
        # remote queries
        qf = QueryFinisher(self.consumer,
                           self.discovery,
                           URLUtils.serialize_space_to_URL(),
                           URLUtils.serialize_wildcard_to_URL(template),
                           sim = self.simulation)
        # when I've tried to do it in the same class (qf = self), some of the activation weren't really activated
        # may be because a method of the same object cannot be used at the same simulation time?
        # In this case, when they overlap, the activation of _finish_query_waiting may be ignored when they overlap in time
        self.simulation.activate(qf, qf._finish_query_waiting(template)) # to wait for whitepages

    def recover_from_drop(self):
        # after a drop I won't be WP anymore
        if self.whitepage is not None:
            self.whitepage.stop()
        
        # setting to None helps to answer correct 501 answer on the server-side
        self.whitepage = None

    def stop(self):
        if self.provider is not None:
            self.provider.stop()
        
        if self.consumer is not None:
            self.consumer.stop()

class QueryFinisher(Process, RequestObserver):
    
    def __init__(self, consumer, discovery, fromSpaceToURL, fromTemplateToURLtemplate, sim=None):
        super(QueryFinisher, self).__init__(sim=sim)
        self.consumer = consumer
        self.discovery = discovery
        self.fromSpaceToURL = fromSpaceToURL
        self.fromTemplateToURLtemplate = fromTemplateToURLtemplate
    
    def _finish_query_waiting(self, template):
        # TODO local query
        
        selected_nodes = None
        previously_unsolved = True
        attempts = 5 # to avoid too many process on memory when no clue has been checked
        while selected_nodes is None and attempts>0:
            try:
                selected_nodes = self.consumer.get_query_candidates(template, previously_unsolved)
                previously_unsolved = False
            except Exception as e:
                #print "Waiting for a whitepage (t=%d)."%(self.sim.now()), e.args[0]
                attempts -= 1
            if selected_nodes is None and attempts>0:
                yield hold, self, 100
            
        if attempts==0:
            # somehow record this failure
            print "No clues have been initialized in %s (t=%d)." % ( self.discovery.get_my_record().node_name, self.sim.now() )
            #pass
        else:
            try:
                if len(selected_nodes)>0:
                    destNodes = []
                    for node_name in selected_nodes:
                        if node_name!=self.discovery.me.name: # local query already done
                            destNodes.append(NodeManager.getNodeByName(node_name))
                    
                    req = RequestInstance(self.discovery.me, destNodes,
                                          '/' + self.fromSpaceToURL + "query/" + self.fromTemplateToURLtemplate,
                                          name = "queryAt"+str(self.sim.now()),
                                          sim = self.sim )
                    RequestManager.launchNormalRequest(req)
            except:
                import traceback
                traceback.print_exc()
                raise
    
    def notifyRequestFinished(self, request_instance):
        pass # do I really need the results?