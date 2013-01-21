'''
Created on Sep 17, 2012

@author: tulvur
'''

import weakref
from abc import ABCMeta, abstractmethod
from SimPy.Simulation import Process, SimEvent, waitevent
from netuse.sim_utils import Timer
from clueseval.clues.versions.management import Version
from clueseval.clues.node_attached import ClueWithNode
from netuse.triplespace.network.discovery.discovery import DiscoveryEventObserver
from netuse.triplespace.our_solution.provider.simple_clue_management import ClueManager
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver


class Provider(Process, DiscoveryEventObserver):
    
    RETRY_ON_FAILURE = 10000 # 10 secs
    UPDATE_TIME = 3600000 # 1h
    
    def __init__(self, dataaccess, discovery, sim=None):
        super(Provider, self).__init__(sim=sim)
        
        self.discovery = discovery
        self.discovery.add_changes_observer(self)
        self.clue_manager = ClueManager(dataaccess)
        
        self.__stop = False
        self.wp_node_name = None
        self.connector = None
        
        self.externalCondition = SimEvent(name="external_condition_on_%s"%(self.name), sim=sim)
        self.clueChanged = SimEvent(name="clue_change_on_%s"%(self.name), sim=sim)
        self.stopProvider = SimEvent(name="stop_provider_%s"%(self.name), sim=sim)
        self.timer = None
        
        self.last_contribution_to_aggregated_clue = Version(-1, -1)
        self.alive_for_external_condition = False
    
    def update_clues_on_whitepage(self):
        remaining = 0
        sleep_for = 0
        while not self.__stop:
            if self.alive_for_external_condition:
                # only if I have a Version the new WP does not have
                new_wp_r = self.discovery.get_whitepage_record()
                if new_wp_r is None:
                    sleep_for = Provider.RETRY_ON_FAILURE
                else:
                    if self.last_contribution_to_aggregated_clue > new_wp_r.version:
                        retry = self.sent_through_connector()
                        sleep_for = Provider.UPDATE_TIME if not retry else Provider.RETRY_ON_FAILURE
                    else:
                        # nothing to send, the Provider can continue sleeping
                        # as if nothing happened
                        sleep_for = remaining if remaining > 0 else Provider.UPDATE_TIME
                self.alive_for_external_condition = False # for the next iteration
            else:
                # last clue has expired or it has changed => send it to the WP
                retry = self.sent_through_connector()
                sleep_for = Provider.UPDATE_TIME if not retry else Provider.RETRY_ON_FAILURE
            
            self.timer = Timer(sleep_for, sim=self.sim)
            self.sim.activate(self.timer, self.timer.wait())
            
            before = self.sim.now()
            yield waitevent, self, (self.timer.event, self.externalCondition, self.clueChanged, self.stopProvider)
            remaining = Provider.UPDATE_TIME - (self.sim.now() - before)
    
    def sent_through_connector(self):
        """Returns if it needs to be retry or not."""
        self.__update_connector_if_needed()
        if self.connector is not None:
            self.connector.send_clue(self.clue_manager.get_clue())
        return self.connector is None # if the connector could not be updated, retry
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if wp!=None:
            # TODO reuse connectors as done in "consumer" module
            if self.wp_node_name==None or self.wp_node_name!=wp.name:
                self.wp_node_name = wp.name
                if wp==self.discovery.me:
                    self.connector = LocalConnector(self.discovery, self)
                else:
                    self.connector = RemoteConnector(self.discovery.me, wp, self.sim, self)
                    
    def refresh_clue(self):
        refreshed = self.clue_manager.refresh()
        if refreshed:
            self.clueChanged.signal()
    
    def on_whitepage_selected_after_none(self):
        if self.timer==None: self.cancel(self.timer)
        self.alive_for_external_condition = True
        self.externalCondition.signal()
    
    # Just in case
    def stop(self):
        self.__stop = True
        self.stopProvider.signal()
        
    def set_last_version(self, version):
        self.last_contribution_to_aggregated_clue = version


class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, observer):
        self.observer = weakref.proxy(observer)
    
    @abstractmethod
    def send_clue(self, clue):
        pass


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery, observer):
        super(LocalConnector, self).__init__(observer)
        self.local_whitepage = discovery.me.ts.whitepage
        self.me = discovery.me
        
    def send_clue(self, clue):
        # TODO a method to add local clues to the store without serializing/parsing
        cwn = ClueWithNode(self.me.name, clue)
        self.local_whitepage.add_clue(self.me.name, cwn.toJson()) # non-sense: serialize to parse
        self.observer.set_last_version( self.local_whitepage.clues.version )


class RemoteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node, simulation, observer):
        super(RemoteConnector, self).__init__(observer)
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.simulation = simulation
    
    def send_clue(self, clue):
        RequestManager.launchNormalRequest(self._get_update_request(clue))
    
    def _get_update_request(self, clue):
        c = ClueWithNode(self.me_as_node.name, clue)
        req = RequestInstance( self.me_as_node,
                               [self.whitepage_node],
                               '/whitepage/clues/' + self.me_as_node.name,
                               data = c.toJson(),
                               sim = self.simulation )
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                last_version = Version.create_from_json( unique_response.get_data() )
                self.observer.set_last_version( last_version )