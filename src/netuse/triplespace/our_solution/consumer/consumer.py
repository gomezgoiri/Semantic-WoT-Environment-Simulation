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

from abc import ABCMeta, abstractmethod
from netuse.triplespace.our_solution.whitepage.selection import WhitepageSelector, WhitepageSelectionManager, SelectionProcessObserver


class ConsumerFactory(object):
    
    def __init__(self, simulation, discovery):
        self.simulation = simulation
        self.discovery = discovery
    
    def _canManageClues(self):
        my_drecord = self.discovery.get_my_record()
        # really naive condition
        # TODO enhance and take into account selection module
        return WhitepageSelector._to_bytes(*my_drecord.memory) > WhitepageSelector._to_bytes(*WhitepageSelector.MEMORY_LIMIT)            
    
    def createConsumer(self):
        if self._canManageClues():
            from netuse.triplespace.our_solution.consumer.full import Consumer
            return Consumer(self.simulation, self.discovery)
        else:
            from netuse.triplespace.our_solution.consumer.lite import ConsumerLite
            return ConsumerLite(self.simulation, self.discovery)


class AbstractConsumer(SelectionProcessObserver):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, simulation, discovery):
        self.simulation = simulation
        self.discovery = discovery
        self.connector = None
        self.wsm = None
    
    def get_query_candidates(self, template, previously_unresolved=False):
        keep_waiting = self.__update_connector_if_needed()
        
        if keep_waiting or self.connector is None:
            raise Exception("Try again a little bit latter.")
        return self.connector.get_query_candidates(template, previously_unresolved)
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if wp is None:
            if not self.ongoing_selection:
                # Not setting the SelectionManager as an attribute ruins everything.
                # The object disappears and the result of the sent request
                # is never assigned to "wsm".
                # Consequently, "wsm" never calls to the callback and ongoing_selection
                # returns True for the rest of the simulation.
                self.wsm = WhitepageSelectionManager(self.simulation, self.discovery)
                self.wsm.set_observer(self)
                self.wsm.choose_whitepage(self.get_clue_store())
            return True
        else:
            self._update_connector(wp)
            return False
    
    @abstractmethod
    def _update_connector(self, wp):
        # TODO set directly after a selection without waiting discovery of new WP
        # (we know for sure that it is the new WP!)
        pass
    
    @property
    def ongoing_selection(self):
        return self.wsm is not None
    
    def wp_selection_finished(self, wp_node):
        self.wsm = None
        # TODO update the connector with the new selected white page
    
    def stop(self):
        if self.connector is not None:
            self.connector.stop()
    
    # to initialize the WP if this consumer node becomes WP
    def get_clue_store(self):
        return None



class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_query_candidates(self, template, previously_unresolved):
        pass
    
    def start(self):
        pass

    def stop(self):
        pass