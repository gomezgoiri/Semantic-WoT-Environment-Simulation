'''
Created on Nov 28, 2011

@author: tulvur
'''
from SimPy.Simulation import Resource
from netuse.results import G

# In the future other Device dependent methods can be implemented such as: reasoning
# That's why I've created a Hierarchy instead of just having some variables with the 2D arrays which represent each node
class DeviceType():
    # Waiting time measure in FoxG20
    # Concurrent request, Mean, Std dev    
    def __init__(self, waitingTime=None, canQueue=True, canReason=True):
        self.__wait = waitingTime
        if waitingTime!=None:
            last = len(self.__wait)-1
            self.__resources = Resource(self.__wait[last][0], name="Concurrent requests this node can answer")
            
        # a device can or cannot queue requests
        # we it is able to queue, then no limit is imposed (unbounded queue)
        self.canQueue = canQueue
        self.canReason = canReason
            
    @classmethod
    def create(cls, device_type):
        device_type = device_type.lower()
        if device_type==XBee.TYPE_ID:
            return XBee()
        elif device_type==FoxG20.TYPE_ID:
            return FoxG20()
        elif device_type==RegularComputer.TYPE_ID:
            return RegularComputer()
        else:
            raise Exception('Invalid device type:', device_type)
    
    def getTimeNeededToAnswer(self):
        numConcurrentRequests = self.getCurrentConcurrentRequests()
        
        if numConcurrentRequests==1:
            curr = self.__wait[0]
            responseTime = G.Rnd.normalvariate(curr[1],curr[2])
        else:
            for i in range(1,len(self.__wait)):
                prev = self.__wait[i-1]
                curr = self.__wait[i]
                if numConcurrentRequests<=curr[0]:
                    factor = (numConcurrentRequests-prev[0]) / float(curr[0]-prev[0])
                    avg = round( (curr[1] - prev[1]) * factor + prev[1], 2) # for testing purposes
                    dev = round( (curr[2] - prev[2]) * factor + prev[2], 2) # for testing purposes
                    responseTime = G.Rnd.normalvariate(avg,dev)
                    break
        return responseTime if responseTime>0 else 0.1
    
    def getMaxConcurrentRequests(self):
        return self.__resources.capacity
    
    def getCurrentConcurrentRequests(self):
        return self.__resources.capacity - self.__resources.n
    
    def isOverloaded(self):
        return not self.canQueue and self.__resources.n<=0
    
    def getResources(self):
        return self.__resources


class XBee(DeviceType):
    TYPE_ID = 'xbee'
    
    def __init__(self):
        DeviceType.__init__(self, [[1,77,1],
                                 [5,392,8],
                                 [10,775,8]],
                            canQueue=False,
                            canReason=False)

class FoxG20(DeviceType):
    TYPE_ID = 'foxg20'
    
    def __init__(self):
        DeviceType.__init__(self, [[1,17,0],
                                 [5,97,16],
                                 [10,174,28],
                                 [15,282,43],
                                 [20,375,30],
                                 [25,460,30],
                                 [30,540,35],
                                 [35,632,29]],
                            canQueue=False,
                            canReason=True)
        
# I don't remember which example did we use in senami2012,
# but from 50 to 500 new measures in a new benchmarking have been noted down.
# 5 executions of each test have been perfomed because in each execution the average decreases. 
# For more information, check ConcurrentRequests.jmx
class RegularComputer(DeviceType):
    TYPE_ID = 'computer'
    
    def __init__(self):
        DeviceType.__init__(self, [[1,13,0],
                                 [5,7,3],
                                 [10,8,4],
                                 [15,5,2],
                                 [20,5,3],
                                 [25,5,4],
                                 [30,6,4],
                                 [35,5,2],
                                 [50,42,62],
                                 [100,39,75],
                                 [150,120,156],
                                 [200,169,160],
                                 [250,291,252],
                                 [300,431,373],
                                 [500,769,621]],
                            canQueue=True,
                            canReason=True)