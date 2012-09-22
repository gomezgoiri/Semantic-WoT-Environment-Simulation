'''
Created on Sep 17, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
from SimPy.Simulation import now, hold
from clueseval.clues.aggregated import ClueAggregation
from netuse.triplespace.our_solution.clue_management import ClueStore
from netuse.triplespace.our_solution.consumer.time_update import UpdateTimesManager
from netuse.triplespace.our_solution.whitepage.selection import WhitepageSelectionManager, SelectionProcessObserver
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver

class Consumer(SelectionProcessObserver):
    
    def __init__(self, discovery):
        self.discovery = discovery
        self.connector = None
        self.wp_node_name = None
        self.ongoing_selection = False
    
    def get_query_candidates(self, template, previously_unresolved=False):
        self.__update_connector_if_needed()
        
        if self.connector==None:
            raise Exception("Try again a little bit latter.")
        return self.connector.get_query_candidates(template, previously_unresolved)
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if wp is None:
            if not self.ongoing_selection:
                self.ongoing_selection = True
                wsm = WhitepageSelectionManager(self.discovery)
                wsm.set_observer(self)
                wsm.choose_whitepage()
        else:
            if self.wp_node_name is None or self.wp_node_name!=wp.name:
                self.wp_node_name = wp.name
                if wp==self.discovery.me:
                    self.connector = LocalConnector(self.discovery)
                else:
                    self.connector = RemoteConnector(self.discovery.me, wp)
                    
    def wp_selection_finished(self, wp_node):
        self.ongoing_selection = False
        pass
        # TODO update the connector with the new selected white page


class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_query_candidates(self, template, previously_unresolved):
        pass


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery):
        self.local_whitepage = discovery.me.ts.whitepage
    
    def get_query_candidates(self, template, previously_unresolved):
        return self.local_whitepage.get_query_candidates(template)


class RemoteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.updateTimeManager = UpdateTimesManager()
        
        self.clues = ClueStore()
        
        self._initialize_clues()
        self._schedule_future_update()
    
    def _initialize_clues(self):
        # request to whitepage
        RequestManager.launchNormalRequest(self._get_update_request())
    
    def _schedule_future_update(self):
        up_time = self.updateTimeManager.get_updatetime()
        self.scheduled_request = RequestManager.launchScheduledRequest(self._get_update_request(), now()+up_time)
    
    def _get_update_request(self):
        req = RequestInstance(self.me_as_node, [self.whitepage_node], '/whitepage/clues')
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                ca = ClueAggregation()
                ca.fromJson(unique_response.get_data())
                self.clues.add_clues(ca)
                break
        self._schedule_future_update() # next clue update!
    
    def _check_if_next_update_changes(self):
        possible_next = now() + self.updateTimeManager.get_updatetime()
        # if we don't have a scheduled update or we have a candidate to update our next update with an earlier update...
        if possible_next < self.scheduled_request.at:
            # stop any previously scheduled request, start a new request
            RequestManager.cancelRequest(self.scheduled_request)
            
            # schedule the next update
            self._schedule_future_update()
    
    def get_query_candidates(self, template, previously_unsolved=False):
        if not previously_unsolved:
            self.updateTimeManager.add_updatetime(now()) # add a timestamp of now to get the update frequency
            self._check_if_next_update_changes()
        if not self.clues.started:
            # wait untill the clues are loaded for the first time
            raise Exception("Wait for the first clue loading.")
        return self.clues.get_query_candidates(template)