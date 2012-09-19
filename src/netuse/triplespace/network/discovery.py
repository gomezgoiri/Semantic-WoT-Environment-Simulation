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
    INFINITE_BATTERY = 'inf' # plugged in to the plug
    
    def __init__(self, memory='1MB', storage='1MB',
                 joined_since=1, sac=False, battery_lifetime=INFINITE_BATTERY, is_whitepage=False):
        self.change_observers = []
        self.memory = self._separate_units_from_values(memory) # does not change
        self.storage = self._separate_units_from_values(storage) # does not change
        self.__joined_since = joined_since
        self.__sac = sac
        self.__battery_lifetime = battery_lifetime
        self.__is_whitepage = is_whitepage
        
    def _separate_units_from_values(self, unstandardized):
        i = 0
        for c in unstandardized:
            if not c.isdigit():
                break
            else:
                i += 1
        standardized = (int(unstandardized[:i]), unstandardized[i:].replace(' ', ''))
        return standardized
        
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
    def battery_lifetime(self):
        return self.__battery_lifetime
    
    @battery_lifetime.setter
    def battery_lifetime(self, battery_lifetime):
        self.__battery_lifetime = battery_lifetime
        self.__record_updated()
        
    @property
    def is_whitepage(self):
        return self.__is_whitepage
    
    @is_whitepage.setter
    def is_whitepage(self, is_whitepage):
        self.__is_whitepage = is_whitepage
        self.__record_updated()
    


class DiscoveryRecordObserver(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def notify_changes(self):
        pass


class SimpleDiscoveryMechanism(DiscoveryRecordObserver):
    def __init__(self, me, rest):
        self.me = me
        self.rest = rest
        for node in self.rest:
            node.discovery_record.add_change_observer(self)
    
    def notify_changes(self):
        pass
    
    def get_whitepage(self):
        '''Returns the node currently acting as whitepage. None if no whitepage exists in the space.'''
        if self.me.discovery_record.is_whitepage:
            return self.me
        else:
            for node in self.rest:
                if node.discovery_record.is_whitepage:
                    return node
        return None