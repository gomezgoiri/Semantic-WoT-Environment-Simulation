'''
Created on Nov 26, 2011

@author: tulvur
'''
import copy
from StringIO import StringIO
from itertools import cycle
from rdflib import Graph
from SimPy.Simulation import random
from netuse.nodes import NodeGenerator
from netuse.triplespace.kernel import NegativeBroadcasting, Centralized, OurSolution
from netuse.triplespace.network.discovery.simple import DiscoveryFactory
from netuse.database.parametrization import Parametrization
from netuse.results import G

class ActivityGenerator(object):
    
    def __init__(self, params, baseGraphs, simulation):
        self.FAKE_GRAPH = Graph().parse(StringIO("<http://www.deusto.es/fakesubject> <http://www.deusto.es/fakepredicate> <http://www.deusto.es/fakeobject> .\n"), format="nt")
        self.FAKE_GRAPH.bind("deusto", "http://www.deusto.es/", override=True)
        self.__params = params
        self.__baseGraphs = baseGraphs
        self.__simulation = simulation
        self.__discovery_factory = DiscoveryFactory(NodeGenerator.getNodes())
    
    def generateActivity(self):
        if self.__params.strategy==Parametrization.negative_broadcasting :
            self.configureNegativeBroadcasting()
        elif self.__params.strategy==Parametrization.our_solution :
            self.configureOurSolution()
        elif self.__params.strategy==Parametrization.centralized :
            self.configureCentralizedActivity()
        
        self.generateSimulationWritings()
        self.generateSimulationQueries(self.__params.numConsumers)
    
    def configureNegativeBroadcasting(self):
        for n in NodeGenerator.getNodes():
            discov = self.__discovery_factory.create_simple_discovery(n)
            n.ts = NegativeBroadcasting(discov)
            
    def configureOurSolution(self):
        for n in NodeGenerator.getNodes():
            discov = self.__discovery_factory.create_simple_discovery(n)
            n.ts = OurSolution(discov, self.__simulation) #, self.__baseGraphs['ontology'])
            n.ts.reasoningCapacity = n.canReason
    
    def configureCentralizedActivity(self):
        centralNode = NodeGenerator.getNodes()[0] # for instance
        centralNode.ts = Centralized(centralNode)
        
        rest = list(NodeGenerator.getNodes())
        rest.remove(centralNode)
        for n in rest:
            n.ts = Centralized(n, centralNode)
    
    def generateSimulationWritings(self):        
        if 0 < self.__params.writeFrequency:
            # writings
            for i in range(0,self.__params.numberOfNodes):
                actionNode = NodeGenerator.getNodes()[i]
                graphsToWrite = () if self.__baseGraphs==None or not actionNode.name in self.__baseGraphs else copy.deepcopy(self.__baseGraphs[actionNode.name])                
                # a little bit of randomness to avoid all the nodes writing at the same time
                startsWriting = random.randint(0, self.__params.writeFrequency)
                for writesAt in range(0, int(self.__params.simulateUntil), self.__params.writeFrequency): # starts writing at 10 (for example)
                    if graphsToWrite:
                        last = graphsToWrite.pop()
                    else:
                        last = self.FAKE_GRAPH
                        
                    #print "%s writes at %s"%(actionNode, startsWriting+writesAt)
                    actionNode.ts.write(starts_at=startsWriting+writesAt, simulation=self.__simulation, triples=last)
        
    
    def generateSimulationQueries(self, numConsumers):
        consumerNodes = cycle(G.Rnd.sample(NodeGenerator.getNodes(), numConsumers))
        
        # queries to central node
        if self.__params.numberOfNodes>1: # otherwise it does not make sense!
            for _ in range(self.__params.amountOfQueries):
                startAt = G.Rnd.randint(0,self.__params.simulateUntil)
                template = G.Rnd.choice(self.__params.queries)
                
                requester = consumerNodes.next()
                #print "%s requests at %s"%(requester,startAt)
                requester.ts.query(starts_at=startAt, simulation=self.__simulation, template=template)