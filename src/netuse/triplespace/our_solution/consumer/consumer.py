'''
Created on Sep 17, 2012

@author: tulvur
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
                wsm.choose_whitepage(self.get_clue_store())
        else:
            self._update_connector(wp)
    
    @abstractmethod
    def _update_connector(self, wp):
        # TODO set directly after a selection without waiting discovery of new WP
        # (we know for sure that it is the new WP!)
        pass
                    
    def wp_selection_finished(self, wp_node):
        self.ongoing_selection = False
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