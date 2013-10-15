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

from clueseval.clues.storage.sqlite import SQLiteClueStore
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver
from netuse.triplespace.our_solution.consumer.time_update import UpdateTimesManager
from netuse.triplespace.our_solution.consumer.consumer import AbstractConsumer, AbstractConnector


class Consumer(AbstractConsumer):
    def __init__(self, simulation, discovery):
        super(Consumer, self).__init__( simulation, discovery )
        self.local_connector = True # overwritten in _set_connector_for_the_first_time, but just in case
    
    def _set_connector_for_the_first_time(self, wp):
        if wp==self.discovery.me:
            self.connector = LocalConnector(self.discovery)
            self.connector.start()
            self.local_connector = True
        else:
            self.connector = RemoteConnector(self.discovery.me, wp, simulation=self.simulation)
            self.connector.start()
            self.local_connector = False
    
    def _update_connector(self, wp):
        if self.connector is None: # for the first time
            self._set_connector_for_the_first_time(wp)
        else: # for the Nth time
            if wp==self.discovery.me:
                if not self.local_connector: # otherwise the proper local-connector is already set
                    self.connector.stop() # stop the remote connector first, we go to local now!
                    self.connector = LocalConnector(self.discovery)
                    self.connector.start()
                    self.local_connector = True
            else:
                if self.local_connector:
                    self.connector.stop() # stop the local connector first
                    self.connector = RemoteConnector(self.discovery.me, wp, simulation=self.simulation)
                    self.connector.start()
                    self.local_connector = False
                else: # the WP has changed but it is still remote!
                    # reuse the same connector changing the destination of the queries
                    self.connector.change_whitepage(wp)
    
    def get_clue_store(self):
        if self.connector is not None:
            return self.connector.get_clue_store()
        return None


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery):
        self.discovery = discovery
    
    def get_query_candidates(self, template, previously_unresolved):
        local_whitepage = self.discovery.me.ts.whitepage
        if local_whitepage is None:
            return None # I'm not the WP anymore!
        return local_whitepage.get_query_candidates(template)
    
    # this SHOULD never be called!
    # Why would a WP become into a WP?
    def get_clue_store(self):
        return None


class RemoteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node, simulation):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.updateTimeManager = UpdateTimesManager()
        self.simulation = simulation
        
        # Aspecto discutido en issue #1
        # self.clues = SQLiteClueStore(database_path=G.temporary_path)
        # generation id does not matter, will be ovewritten
        self.clues = SQLiteClueStore(in_memory=True)
        self.first_load_in_store = False
        self.stopped = False
        
    def start(self):
        self.clues.start()
        self._initialize_clues()
        self._schedule_future_update()
        
    def stop(self):
        self.clues.stop()
        self.stopped = True
    
    def change_whitepage(self, whitepage_node):
        self.whitepage_node = whitepage_node
        
        # re-schedule the request to send it to the new whitepage instead to the old one
        RequestManager.cancelRequest(self.scheduled_request)
        self.scheduled_request = self._get_update_request() # to new receiver
        # at the same moment that the previous one
        RequestManager.launchScheduledRequest(self.scheduled_request, self.next_scheduled_at)
    
    def _initialize_clues(self):
        # request to whitepage
        RequestManager.launchNormalRequest(self._get_update_request())
    
    def _schedule_future_update(self):
        up_time = self.updateTimeManager.get_updatetime()
        self.scheduled_request = self._get_update_request()
        self.next_scheduled_at = self.simulation.now() + up_time
        
        RequestManager.launchScheduledRequest(self.scheduled_request, self.next_scheduled_at)
    
    def _get_update_request(self):
        req = RequestInstance( self.me_as_node,
                               [self.whitepage_node],
                               '/whitepage/clues',
                               sim = self.simulation )
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                self.clues.fromJson(unique_response.get_data())
                # update version on discovery record
                # NOT NECESSARY IN CURRENT ALGORITHM, WE CAN AVOID TRAFFIC IN MDNS
                #self.me_as_node._discovery_instance.get_my_record().version = self.clues.version
                self.first_load_in_store = True
            elif unique_response.getstatus()==408 or unique_response.getstatus()==501:
                # if timeout or the node is not a whitepage anymore
                # If it was TIMEOUT, we could retry it
                # To simplify RETRY==0!
                # TODO flush record from this whitepage
                pass
            break
        self._check_if_next_update_changes() # schedule next clue update!
    
    def _check_if_next_update_changes(self):
        if self.next_scheduled_at <= self.simulation.now(): # if last update already done...
            # ...schedule the next one
            self._schedule_future_update()
        else: # one request already scheduled, other may override it
            
            possible_next = self.simulation.now() + self.updateTimeManager.get_updatetime()
            
            # if we  have a candidate to update our next update with an earlier update...
            if possible_next < self.next_scheduled_at:
                # stop any previously scheduled request, start a new request
                RequestManager.cancelRequest(self.scheduled_request)
                
                # schedule the next update
                self._schedule_future_update()
    
    def get_query_candidates(self, template, previously_unsolved=False):
        if not previously_unsolved:
            # add a timestamp of "now" to get the updated frequency
            self.updateTimeManager.add_updatetime( self.simulation.now() )
            self._check_if_next_update_changes()
        if not self.first_load_in_store:
            # wait until the clues are loaded for the first time
            raise Exception("Wait for the first clue loading.")
        
        return self.clues.get_query_candidates(template)
    
    def get_clue_store(self):
        if self.first_load_in_store and not self.stopped:
            return self.clues
        else:
            return None # just in case it has not been even opened/loaded or already closed!