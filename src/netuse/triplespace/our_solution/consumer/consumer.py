'''
Created on Sep 17, 2012

@author: tulvur
'''
import json
from abc import ABCMeta, abstractmethod
from clueseval.clues.storage.sqlite import SQLiteClueStore
from clueseval.clues.storage.memory import MemoryClueStore
from netuse.triplespace.network.url_utils import URLUtils
from netuse.triplespace.our_solution.consumer.time_update import UpdateTimesManager
from netuse.triplespace.our_solution.whitepage.selection import WhitepageSelector, WhitepageSelectionManager, SelectionProcessObserver
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver


class ConsumerFactory(object):
    
    def __init__(self, simulation, discovery):
        self.simulation = simulation
        self.discovery = discovery
    
    def _canManageClues(self):
        my_drecord = self.discovery.me.discovery_record
        # really naive condition
        # TODO enhance and take into account selection module
        return WhitepageSelector._to_bytes(*my_drecord.memory) > WhitepageSelector._to_bytes(*WhitepageSelector.MEMORY_LIMIT)            
    
    def createConsumer(self):
        if self._canManageClues():
            return Consumer(self.simulation, self.discovery)
        else:
            return ConsumerLite(self.simulation, self.discovery)


class AbstractConsumer(SelectionProcessObserver):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, simulation, discovery):
        self.simulation = simulation
        self.discovery = discovery
        self.connector = None
        self.wp_node_name = None
        self.ongoing_selection = False
    
    def get_query_candidates(self, template, previously_unresolved=False):
        self.__update_connector_if_needed()
        
        if self.connector is None:
            raise Exception("Try again a little bit latter.")
        return self.connector.get_query_candidates(template, previously_unresolved)
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if wp is None:
            if not self.ongoing_selection:
                self.ongoing_selection = True
                wsm = WhitepageSelectionManager(self.simulation, self.discovery)
                wsm.set_observer(self)
                wsm.choose_whitepage()
        else:
            self._update_connector(wp)
    
    @abstractmethod
    def _update_connector(self, wp):
        pass
                    
    def wp_selection_finished(self, wp_node):
        self.ongoing_selection = False
        # TODO update the connector with the new selected white page
    
    def stop(self):
        if self.connector is not None:
            self.connector.stop()

class Consumer(AbstractConsumer):
    def _update_connector(self, wp):
        if self.wp_node_name is None or self.wp_node_name!=wp.name:
            if self.connector is not None:
                self.connector.stop()
            
            self.wp_node_name = wp.name
            if wp==self.discovery.me:                
                self.connector = LocalConnector(self.discovery)
            else:
                self.connector = RemoteConnector(self.discovery.me, wp, simulation=self.simulation)
            self.connector.start()

class ConsumerLite(AbstractConsumer):
    def _update_connector(self, wp):
        if self.wp_node_name is None or self.wp_node_name!=wp.name:
            if self.connector is not None:
                self.connector.stop()
            
            self.wp_node_name = wp.name
            if wp==self.discovery.me:
                raise Exception("A lite consumer cannot be whitepage, check the selection algorithm.")
            else:
                self.connector = RemoteLiteConnector(self.discovery.me, wp, simulation=self.simulation)
            self.connector.start()


class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_query_candidates(self, template, previously_unresolved):
        pass
    
    def start(self):
        pass

    def stop(self):
        pass


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery):
        self.local_whitepage = discovery.me.ts.whitepage
    
    def get_query_candidates(self, template, previously_unresolved):
        return self.local_whitepage.get_query_candidates(template)


class RemoteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node, simulation):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.updateTimeManager = UpdateTimesManager()
        self.simulation = simulation
        
        # Aspecto discutido en issue #1
        # self.clues = SQLiteClueStore(database_path=G.temporary_path)
        self.clues = SQLiteClueStore(in_memory=True)
        self.first_load_in_store = False
        
    def start(self):
        self.clues.start()
        self._initialize_clues()
        self._schedule_future_update()
        
    def stop(self):
        self.clues.stop()
    
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
                self.first_load_in_store = True
                break
            else:
                # TODO
                # If it has not been received, the next request should be quickly,
                # otherwise the node is going to wait too much if the WP
                # is just setting up and receiving clues for the first time!
                pass
        self._check_if_next_update_changes() # next clue update!
    
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


class RemoteLiteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node, simulation):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.simulation = simulation
        self.responses = {}
    
    def _get_candidates_from_wp_request(self, templateURL):
        req = RequestInstance( self.me_as_node,
                               [self.whitepage_node],
                               '/whitepage/clues/query/%s'%(templateURL),
                               sim = self.simulation )
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                # get the template URL requested
                pattern = "/whitepage/clues/query/"
                path = unique_response.geturl()
                pos = path.find(pattern) + len(pattern) # it could be len(pattern) since pattern will be always at the begining
                templateURL = path[pos:]
                
                # parse a list of names (nodes)
                list_candidates = json.loads(unique_response.get_data())
                self.responses[templateURL] = list_candidates
                
                break
            else:
                # TODO
                # What has happened? How to solve it?
                pass
    
    def get_query_candidates(self, template, previously_unsolved=False):
        templateURL = URLUtils.serialize_wildcard_to_URL(template)
        
        if templateURL in self.responses.keys():
            if self.responses[templateURL]==None:
                raise Exception("Wait for the answer.")
            else:
                # take the response
                candidates = self.responses[templateURL]
                del self.responses[templateURL]
                return candidates
        else:
            self.responses[templateURL] = None # create a slot to store the response later and warn that it's being requested until then
            RequestManager.launchNormalRequest(self._get_candidates_from_wp_request(templateURL))
            return None # waiting for it