'''
Created on Nov 26, 2011

@author: tulvur
'''
import copy
from StringIO import StringIO
from itertools import cycle
from rdflib import Graph
from SimPy.Simulation import random
from abc import abstractmethod, ABCMeta
from netuse.nodes import NodeGenerator
from netuse.network_models import NetworkModelManager
from netuse.triplespace.kernel import NegativeBroadcasting, Centralized, OurSolution
from netuse.triplespace.network.discovery.simple import DiscoveryFactory
from netuse.database.parametrization import Parametrization
from netuse.results import G

class ActivityGenerator(object):
    
    @staticmethod
    def create(params, baseGraphs, simulation):
        activity = None
        
        if params.strategy==Parametrization.negative_broadcasting :
            activity = NegativeBroadcastingActivity(params, baseGraphs, simulation)
        elif params.strategy==Parametrization.our_solution :
            activity = OurSolutionActivity(params, baseGraphs, simulation)
        elif params.strategy==Parametrization.centralized :
            activity = CentralizedActivity(params, baseGraphs, simulation)
        else:
            raise Exception("Unrecognized strategy.")
        
        activity.generate_activity()


class AbstractActivity(object):
    """
    Class in charge of creating the activity scheduled for a certain simulation.
    
    More activity may be generated during the simulation as a consequence of this activity.
    But the activity generated by this class is going to be generated "per se" before calling to Simpy's "simulate" method.
    """    
    __metaclass__ = ABCMeta
    
    def __init__(self, params, baseGraphs, simulation):
        self.FAKE_GRAPH = Graph().parse(StringIO("<http://www.deusto.es/fakesubject> <http://www.deusto.es/fakepredicate> <http://www.deusto.es/fakeobject> .\n"), format="nt")
        self.FAKE_GRAPH.bind("deusto", "http://www.deusto.es/", override=True)
        self._params = params
        self._baseGraphs = baseGraphs
        self._simulation = simulation
        self._discovery_factory = DiscoveryFactory(NodeGenerator.getNodes())
    
    @abstractmethod
    def _configure_nodes(self):
        pass
    
    def generate_activity(self):
        self._configure_nodes()
        NetworkModelManager.run_model(model="normal")
        self._generateSimulationWritings()
        self._generateSimulationQueries(self._params.numConsumers)
        
        
    def _generateSimulationWritings(self):        
        if 0 < self._params.writeFrequency:
            # writings
            for i in range(0,self._params.numberOfNodes):
                actionNode = NodeGenerator.getNodes()[i]
                graphsToWrite = () if self._baseGraphs==None or not actionNode.name in self._baseGraphs else copy.deepcopy(self._baseGraphs[actionNode.name])                
                # a little bit of randomness to avoid all the nodes writing at the same time
                startsWriting = random.randint(0, self._params.writeFrequency)
                for writesAt in range(0, int(self._params.simulateUntil), self._params.writeFrequency): # starts writing at 10 (for example)
                    if graphsToWrite:
                        last = graphsToWrite.pop()
                    else:
                        last = self.FAKE_GRAPH
                        
                    #print "%s writes at %s"%(actionNode, startsWriting+writesAt)
                    actionNode.ts.write(starts_at=startsWriting+writesAt, simulation=self._simulation, triples=last)
        
    
    def _generateSimulationQueries(self, numConsumers):
        consumerNodes = cycle(G.Rnd.sample(NodeGenerator.getNodes(), numConsumers))
        
        # queries to central node
        if self._params.numberOfNodes>1: # otherwise it does not make sense!
            for _ in range(self._params.amountOfQueries):
                startAt = G.Rnd.randint(0,self._params.simulateUntil)
                template = G.Rnd.choice(self._params.queries)
                
                requester = consumerNodes.next()
                #print "%s requests at %s"%(requester,startAt)
                requester.ts.query(starts_at=startAt, simulation=self._simulation, template=template)


class NegativeBroadcastingActivity(AbstractActivity):
    
    def _configure_nodes(self):
        for n in NodeGenerator.getNodes():
            discov = self._discovery_factory.create_simple_discovery(n)
            n.ts = NegativeBroadcasting(discov)

class OurSolutionActivity(AbstractActivity):       
    def _configure_nodes(self):
        for n in NodeGenerator.getNodes():
            discov = self._discovery_factory.create_simple_discovery(n)
            n.ts = OurSolution(discov, self._discovery_factory) #, self._baseGraphs['ontology'])
            n.ts.reasoningCapacity = n.canReason

class CentralizedActivity(AbstractActivity):
    def _configure_nodes(self):
        centralNode = NodeGenerator.getNodes()[0] # for instance
        centralNode.ts = Centralized(centralNode)
        
        rest = list(NodeGenerator.getNodes())
        rest.remove(centralNode)
        for n in rest:
            n.ts = Centralized(n, centralNode)