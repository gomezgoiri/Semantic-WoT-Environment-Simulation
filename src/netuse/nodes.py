'''
Created on Nov 26, 2011

@author: tulvur
'''
from SimPy.Simulation import Process, Resource, passivate, hold, release, request
import weakref
from netuse.sim_utils import schedule, activatable
from devices import RegularComputer
from netuse.triplespace.network.discovery.record import DiscoveryRecord
from netuse.triplespace.network.server import CustomSimulationHandler


class NodeManager(object):
    
    nodes = {}
    
    def __init__(self, params, simulation):
        self.__params = params
        self.__simulation = simulation
        NodeManager.nodes = {}
    
    @staticmethod
    def getNodes():
        return NodeManager.nodes.values()
    
    @staticmethod
    def getNodeByName(node_name):
        return NodeManager.nodes[node_name]


class ConcurrentThread(Process):
        
    def __init__(self, node, device, connections, sim, name="thread"):
        super(ConcurrentThread, self).__init__(name=name, sim=sim)
        self.__node = weakref.proxy(node)
        self.__device = device
        self.__connections = connections
    
    def executeTask(self, handler, req):
        if self.__node.down:
            # do nothing, force the timeout on the client
            pass
        elif self.__connections.is_overloaded():
            self.__node.addResponse(handler.handle(req))
        else:
            yield request, self, self.__connections
            
            # do sth
            # complete the simulation with timeNeeded
            yield hold, self, self.__device.get_time_needed_to_answer( self.__connections.get_current_requests() )
            
            yield release, self, self.__connections
            self.__node.addResponse(handler.handle(req))


class Connections(Resource):
    
    def __init__(self, device, sim, name="connections"):
        super(Connections, self).__init__( device.get_maximum_concurrent_requests() ,
                                           name=name,
                                           sim=sim )
        self.canQueue = device.canQueue
    
    def get_current_requests(self):
        return self.capacity - self.n
    
    def is_overloaded(self):
        return not self.canQueue and self.n<=0


class Node(Process):
    
    @property
    def ts(self):
        return self._ts
    
    @ts.setter
    def ts(self, ts_strategy):
        self._ts = ts_strategy
        self._ts.reasoningCapacity = self.__device.canReason
        # Considerations on the handler:
        #  1. It should be defined on each type of kernel just if it changes
        #     from an implementation to another, which is not currently the case.
        #  2. We can create a new handler for each request or share the same handler.
        #     In absence of better arguments, we use the second alternative to save resources.
        self._http_handler = CustomSimulationHandler(ts_strategy)
        self._ts.discovery = self._discovery_instance # sets the discovery instance
    
    @ts.deleter
    def ts(self):
        del self._ts
        
    @property
    def canReason(self):
        return self.__device.canReason
    
    def __init__(self, name="node", discovery_factory=None, device=None, joined_since=1, sac=False, battery_lifetime=1, sim=None):
        super(Node, self).__init__(name=name, sim=sim)
        self._ts = None
        self._http_handler = None
        self.__device = device if device!=None else RegularComputer() # device type 
        self.__connections = Connections( self.__device, sim = sim, name = "%s's connections"%(name) )
        
        discovery_record = DiscoveryRecord(node_name = name,
                                                memory = self.__device.ram_memory,
                                                storage = self.__device.storage_capacity,
                                                joined_since = joined_since,
                                                sac = sac,
                                                battery_lifetime = battery_lifetime if self.__device.hasBattery else DiscoveryRecord.INFINITE_BATTERY)
        self._discovery_instance = discovery_factory.create_simple_discovery(discovery_record)
        
        self.__httpIn = []
        self.__reqIdGenerator = 0
        self.__waitingRequesters_and_InitTime = {} # TODO the "InitTime" is not longer used in this class
        self.down = False # is node down, unreachable, etc.?
    
    @activatable
    def processRequests(self):
        while 1:
            if not self.__httpIn: # if it's empty...
                yield passivate, self
            else:
                # reqIdGenerator was not intended to be used to generate a name for CurrentThread, but I've reused :-P
                thMngr = ConcurrentThread( self,
                                           self.__device,
                                           self.__connections,
                                           name = "%s_th%d"%(self.name, self.__reqIdGenerator),
                                           sim = self.sim)
                self.sim.activate(thMngr, thMngr.executeTask(self._http_handler, self.__httpIn.pop()))
        
    def addResponse(self, response):        
        requester, _ = self.__waitingRequesters_and_InitTime[response.getid()]
        del self.__waitingRequesters_and_InitTime[response.getid()]
        
        requester.addResponse(response)
    
    def queueRequest(self, requester, req):        
        self.__httpIn.append(req)
        self.__waitingRequesters_and_InitTime[req.getid()] = (requester, self.sim.now())
        self.sim.reactivate(self) # starts answering

    def stop(self):
        self._ts.stop()
    
    @schedule
    def swap_state(self):
        """If the node is alive, it goes down. Otherwise, it goes up."""
        self.down = not self.down
        if not self.down: # if the node goes up
            self._discovery_instance.get_my_record().is_whitepage = False # not anymore
            # What if nobody is WP right now?
            # After this notification of the former WP and taking into account that there is no WP,
            # the selection process will be restarted by a consumer. 
    
    def __str__(self):
        return self.name