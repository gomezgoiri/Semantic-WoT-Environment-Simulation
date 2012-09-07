'''
Created on Nov 29, 2011

@author: tulvur
'''
from SimPy.Simulation import *
import nodes
from netuse.results import G

class Stats(Process):
    
    def __init__(self, parameters, nodeGenerator, name="stats"):
        Process.__init__(self, name=name)
        self.__independentVariables = parameters
        self.__nodeGenerator = nodeGenerator
        
    def onSimulationEnd(self, simulationEnd):
        yield hold, self, 0 # to enable this method to be activated in SimPy
        for node in nodes.NodeGenerator.getNodes():
            reactivate(node, simulationEnd+450) # to compute the last inactivity period
            
    def getInactivityAverage(self):
        totalInactivity = Monitor()
        for node in nodes.NodeGenerator.getNodes():
            self.substractActivityFromInactivity(node.getInactivityMonitor(), node.getActivityMonitor())
            totalInactivity.observe(node.getInactivityMonitor().total())
            
        return totalInactivity.mean()  
    
    # is mocked in the unit test
    def __is_significant(self, t):
        return t>5 # to ignore really small amount of "inactivities" and improve the time
    
    def substractActivityFromInactivity(self, inactivityMon, activityMon):        
        def filterInAMonitor(inMonitor):
            filtered = []
            for m in inMonitor:
                if not self.__is_significant(m[yindex]):
                    filtered.append(m)
            for f in filtered:
                inMonitor.remove(f)
        
        
        tindex = 0
        yindex = 1
        
        filterInAMonitor(inactivityMon) # filter(is_significant, inactivityMon) returns a list!
        
        for measure in activityMon:
            lowerAct = measure[tindex] - measure[yindex]
            upperAct =  measure[tindex]
            removeList = []
            for measure2 in inactivityMon:
                lowerInact = measure2[tindex] - measure2[yindex]
                upperInact =  measure2[tindex]
                if lowerAct<lowerInact and upperAct<lowerInact:
                    pass # too low
                elif upperInact<lowerAct and upperInact<upperAct:
                    pass # too high
                elif lowerAct<lowerInact:
                    if upperInact>=upperAct:
                        #   |----------|      (activity)
                        #        |----------| (inactivity)
                        newLowerInact = upperAct
                        measure2[yindex] = upperInact - newLowerInact
                    else: # upperAct>upperInact 
                        #   |----------|      (activity)
                        #      |----|         (inactivity)
                        removeList.append(measure2)
                else: # lowerAct>=lowerInact
                    #       |---|      (activity)
                    #   |----------|   (inactivity)
                    if upperAct<upperInact:
                        removeList.append(measure2)
                        inactivityMon.observe(lowerAct-lowerInact,t=lowerAct)
                        inactivityMon.observe(upperInact-upperAct,t=upperInact)
                    else: #upperAct>=upperInac
                        #       |----------|      (activity)
                        #   |----------|   (inactivity)
                        newUpperInact = lowerAct
                        measure2[tindex] = newUpperInact
                        measure2[yindex] = newUpperInact - lowerInact
            
            # otherwise, if you chance the elements of the list you are iterating in, it does not iterates properly
            for msr in removeList:
                inactivityMon.remove(msr)
        
    def getCountResponses(self, resplist):
        counter = {'ok': 0,
                    'not-found': 0,
                    'server-error': 0}
        for request in resplist:
            for response in request.responses:
                if response.getstatus()==200:
                    counter['ok']+=1
                elif response.getstatus()==404:
                    counter['not-found']+=1
                elif response.getstatus()>=500 and response.getstatus()<600:
                    counter['server-error']+=1
        
        return counter
    
    def countTimeouts(self, timeoutlist):
        count = 0
        for timeoutAmount in timeoutlist:
            count+=timeoutAmount
        return count
    
    def getExecutionInfo(self):
        response_counter = self.getCountResponses(G.executionData.requests["success"]+G.executionData.requests["failure"])
        
        return {
                    "params": self.__independentVariables, 
                    "inactive_period": 0, # Stats.getInactivityAverage(), # FIXME
                    "requests": {
                                 "found": response_counter['ok'],
                                 "not-found": response_counter['not-found'],
                                 "server-error": G.executionData.requests['server-error'],
                                 "timeout": self.countTimeouts(G.executionData.requests["timeout"]), # we have timeouts only when we got failures
                                 "success": len(G.executionData.requests["success"]), # if all the responses were successful
                                 "failure": len(G.executionData.requests["failure"]), # if at least a response was unsuccessful
                                 "total": self.__nodeGenerator.getTotalRequests()
                                 },
                    "data-exchanged": G.executionData.requests["data-exchanged"],
                    "time_needed": 0 if not G.executionData.response_time_monitor else G.executionData.response_time_monitor.mean()
                }