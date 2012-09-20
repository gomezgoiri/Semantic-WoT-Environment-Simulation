
import numpy

class UpdateTimesManager(object):
    
    '''
    This class can be used both from the consumer or from the provider.
    
    Consumer: to decide when it needs to update an aggregated clue from the Whitepage (depending on how much has query).
    Provider: to decide when it should update its clue on the Whitepage (depending on how often it has written sth new). 
    '''
    
    LAST_UPDATES = 10
    MAX_UPDATE_RATE = 600000
    MIN_UPDATE_RATE = 60000
    DEFAULT_UPDATE_TIME = MAX_UPDATE_RATE
    
    def __init__(self):
        self.last_updates = []
        self.observers = []

    def add_updatetime(self, time):
        if len(self.last_updates)<UpdateTimesManager.LAST_UPDATES:
            self.last_updates.append(time)
        else:
            del self.last_updates[0]
            self.last_updates.append(time)
            
    def get_updatetime(self):
        if len(self.last_updates)<2:
            return UpdateTimesManager.DEFAULT_UPDATE_TIME
        else:
            mean_diff = numpy.mean([self.last_updates[i]-self.last_updates[i-1] for i in range(1,len(self.last_updates))])
            
            if mean_diff>UpdateTimesManager.MAX_UPDATE_RATE:
                return UpdateTimesManager.MAX_UPDATE_RATE
            elif mean_diff<UpdateTimesManager.MIN_UPDATE_RATE:
                return UpdateTimesManager.MIN_UPDATE_RATE
            else:
                return mean_diff