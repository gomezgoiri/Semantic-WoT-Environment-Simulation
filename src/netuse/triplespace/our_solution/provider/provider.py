'''
Created on Sep 17, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod
from SimPy.Simulation import Process, SimEvent, activate, hold, waitevent
from clueseval.clues.node_attached import ClueWithNode
from netuse.triplespace.network.discovery import SimpleDiscoveryObserver
from netuse.triplespace.our_solution.provider.simple_clue_management import ClueManager
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver


class Timer(Process):
    def __init__(self, waitUntil=10000.0, name="timer"):
        Process.__init__(self, name=name)
        self.__timeout = waitUntil
        self.event = SimEvent()
        self.ended = False
        
    def wait(self):
        yield hold, self, self.__timeout
        self.ended = True
        self.event.signal()

class Provider(Process, SimpleDiscoveryObserver):
    
    RETRY_ON_FAILURE = 10000 # 10 secs
    UPDATE_TIME = 3600000 # 1h
    
    def __init__(self, dataaccess, discovery):
        Process.__init__()
        
        self.discovery = discovery
        self.clue_manager = ClueManager(dataaccess)
        
        self.stop = False
        self.connector = None
        
        self.externalCondition = SimEvent()
        self.timer = None
    
    def update_clues_on_whitepage(self):
        while not self.stop:
            self.__update_connector_if_needed()
            if self.connector==None:
                self.connector.send_clue(self.clue_manager.get_clue())
            self.timer = Timer(Provider.UPDATE_TIME)
            activate(self.timer, self.timer.wait())
            yield waitevent, self, (self.timer.event, self.externalCondition)
    
    def __update_connector_if_needed(self):
        wp = self.discovery.get_whitepage()
        if wp!=None:
            if self.wp_node_name==None or self.wp_node_name!=wp.name:
                self.wp_node_name = wp.name
                if wp==self.discovery.me:
                    self.connector = LocalConnector(self.discovery)
                else:
                    self.connector = RemoteConnector(self.discovery.me, wp)
                    
    def refresh_clue(self):
        self.clue_manager.refresh()
    
    def on_whitepage_selected_after_none(self):
        if self.timer==None: self.cancel(self.timer)  
        self.externalCondition.signal()


class AbstractConnector(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def send_clue(self, clue):
        pass


class LocalConnector(AbstractConnector):
    
    def __init__(self, discovery):
        self.local_whitepage = self.discovery.me.ts.whitepage
        self.me = self.discovery.me
        
    def send_clue(self, clue):
        self.local_whitepage.add_clue(self.me, clue)


class RemoteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
    
    def send_clue(self, clue):
        RequestManager.launchNormalRequest(self._get_update_request(clue.toJson()))
    
    def _get_update_request(self, clue):
        c = ClueWithNode(self.me_as_node.name, clue)
        req = RequestInstance(self.me_as_node, [self.whitepage_node], '/whitepage/clues/'+self.me_as_node.name, data=c.toJson())
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                # update(self.clues, unique_req) # somehow
                pass # TODO