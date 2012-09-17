'''
Created on Sep 17, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
from SimPy.Simulation import *
from netuse.triplespace.our_solution.clue_management import ClueStore
from netuse.triplespace.our_solution.consumer.time_update import UpdateTimesManager
from netuse.triplespace.network.client import RequestInstance, ScheduledRequest, RequestObserver

class Consumer(object):
    
    def __init__(self, discovery):
        self.discovery = discovery
        self.connector = None
        self.wp_node_name = None
    
    def get_query_candidates(self, template):
        self.__update_connector_if_needed()
        return self.connector.get_query_candidates(template)
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if self.wp_node_name==None or self.wp_node_name!=wp.name:
            self.wp_node_name = wp.name
            if wp==self.discovery.me:
                self.connector = LocalConnector()
            else:
                self.connector = RemoteConnector(self.discovery.me, wp)


class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_query_candidates(self, template):
        pass


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery):
        self.local_whitepage = self.discovery.me.ts.whitepage
        
    def get_query_candidates(self, template):
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
        req = self._get_update_request()
        activate(req, req.startup())
        
    def _schedule_future_update(self):
        up_time = self.updateTimeManager.get_updatetime()
        self.scheduled_request_time = now() + up_time
        self.scheduled_request = ScheduledRequest(self._get_update_request(), up_time)
    
    def _get_update_request(self):
        req = RequestInstance(self.me_as_node, [self.whitepage_node], '/whitepage/clues')
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_req in request_instance.responses:
            # update(self.clues, unique_req) # somehow
            pass # TODO
    
    def _check_if_next_update_changes(self):
        possible_next = now() + self.updateTimeManager.get_updatetime()
        # if we don't have a scheduled update or we have a candidate to update our next update with an earlier update...
        if possible_next < self.scheduled_request_time:
            # stop any previously scheduled request, start a new request
            pc = ProcessCanceler(self.scheduled_request)
            activate(pc, pc.cancel())
            
            # schedule the next update
            self._schedule_future_update()
    
    def get_query_candidates(self, template):
        self.updateTimeManager.add_updatetime(now()) # add a timestamp of now to get the update frequency
        self._check_if_next_update_changes()
        return self.clues.get_query_candidates(template)


class ProcessCanceler(Process):
    def __init__(self, victimProcess):
        Process.__init__(self)
        self.victimProcess = victimProcess
        
    def cancel(self):
        yield hold, self, 0 # the activator function of a Process should be a generator (contain a yield)
        self.cancel(self.victimProcess)