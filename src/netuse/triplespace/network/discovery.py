'''
Created on Sep 16, 2012

@author: tulvur
'''

from abc import ABCMeta, abstractmethod


class DiscoveryFactory(object):
    
    def __init__(self, nodes):
        self.nodes = nodes
        
    def create_simple_discovery(self, localNode):
        restOfTheNodes = list(self.nodes)
        restOfTheNodes.remove(localNode) # substract localNode from the original list and create
        return SimpleDiscoveryMechanism(localNode, restOfTheNodes)


class DiscoveryRecord(object):
    INFINITE_BATERY = 'inf' # plugged in to the plug
    
    def __init__(self, memory='1MB', storage='1MB',
                 joined_since=1, sac=False, batery_lifetime=INFINITE_BATERY):
        self.change_observers = []
        self.memory = memory # does not change
        self.storage = storage # does not change
        self.__joined_since = joined_since
        self.__sac = sac
        self.__batery_lifetime = batery_lifetime
        
    def add_change_observer(self, observer):
        self.change_observers.append(observer)

    def __record_updated(self):
        for observer in self.change_observers:
            observer.notify_changes()
        
    @property
    def sac(self):
        return self.__sac
    
    @sac.setter
    def sac(self, sac):
        self.__sac = sac
        self.__record_updated()
    
    @sac.deleter
    def sac(self):
        del self.__sac
    
    @property
    def joined_since(self):
        return self.__joined_since
    
    @joined_since.setter
    def joined_since(self, joined_since):
        self.__joined_since = joined_since
        self.__record_updated()
    
    @property
    def batery_lifetime(self):
        return self.__batery_lifetime
    
    @joined_since.setter
    def joined_since(self, batery_lifetime):
        self.__batery_lifetime = batery_lifetime
        self.__record_updated()


class DiscoveryRecordObserver(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def notify_changes(self):
        pass


class SimpleDiscoveryMechanism(object, DiscoveryRecordObserver):
    def __init__(self, me, rest):
        self.me = me
        self.rest = rest
        for node in self.rest:
            node.discovery_record.add_change_observer(self)
    
    def notify_changes(self):
        pass