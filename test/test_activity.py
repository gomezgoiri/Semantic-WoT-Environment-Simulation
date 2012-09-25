'''
Created on Nov 30, 2011

@author: tulvur
'''
import unittest
from SimPy.SimulationTrace import *
from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.parametrization import Parametrization
from netuse.results import G
from netuse.statistic import Stats


class TestStrategies(unittest.TestCase):
    
    def setUp(self):
        G.Rnd = random.Random(12346)
    
    def performSimulation(self, parameters):
        trace.tchange(outfile=open(r"/tmp/simulation.log","w"))
        trace.ttext("New simulation!")
        initialize()
        G.newExecution()
        
        nodes = NodeGenerator(parameters)
        nodes.generateNodes()
        
        activity = ActivityGenerator(parameters, G.dataset_path)
        activity.generateActivity()
        
        stats = Stats(parameters, nodes)
        #stats.onSimulationEnd(simulationEnd=parameters.simulateUntil)
        
        simulate(until=parameters.simulateUntil+500)
        
        return stats.getExecutionInfo()
    
    def generateParams(self, s, q, nn, wf=1000):
        return Parametrization(strategy=s,
                               amountOfQueries=q,
                               writeFrequency=wf,
                               nodes = [ "node"+str(i) for i in range(nn) ],
                               simulateUntil = 10000)
        
    def assertCorrectNegativeBroadcasting(self, n, q):
            par = self.generateParams(Parametrization.negative_broadcasting, q, n)
            stats = self.performSimulation(par)
            self.assertEquals( (n-1)*q, stats["requests"]["total"],
            "expected: "+str((n-1)*q)+", got: "+str(stats["requests"]["total"])+" (n:"+str(n)+",q:"+str(q)+"); ")
    
    def test_negativeBroadcasting(self):
        for q in (1,10,100,):
            for n in (1,2,10,100,):
                self.assertCorrectNegativeBroadcasting( n, q )
                
    def assertCorrectCentralized(self, n, q, writeFreq):
        par = self.generateParams(Parametrization.centralized, q, n, writeFreq)
        stats = self.performSimulation(par)
        w =  par.simulateUntil / par.writeFrequency
        
        amountOfMessagesWithoutInitialWritings = 0 if n==1 else q + w*(n-1) # queries + periodic writings 
        amountOfMessagesWithInitialWritings = 0 if n==1 else q + w*(n-1) + (n-1)*2 # queries + periodic writings + initial writings

        #self.assertEquals(amountOfMessagesWithInitialWritings, stats["requests"]["total"],
        #"expected: " + str(amountOfMessagesWithInitialWritings) + ", " +
        #"got: " + str(stats["requests"]["total"]) + " " + self.printParameters(n,q,writeFreq) + "; ")
        
        # we cannot guarantee the initial writings (it depends on whether a file with content exist
        self.assertTrue(amountOfMessagesWithoutInitialWritings<=stats["requests"]["total"],
                        "expected: >=" + str(amountOfMessagesWithoutInitialWritings) + ", " +
                        "got: " + str(stats["requests"]["total"]) + " " + self.printParameters(n,q,writeFreq) + "; ")
        self.assertTrue(stats["requests"]["total"]<=amountOfMessagesWithInitialWritings,
                        "expected: <=" + str(amountOfMessagesWithoutInitialWritings) + ", " +
                        "got: " + str(stats["requests"]["total"]) + " " + self.printParameters(n,q,writeFreq) + "; ")
        
    def printParameters(self, n, q, writeFreq):
        return "(n:"+str(n)+",q:"+str(q)+",wf:"+str(writeFreq)+")"
    
    def test_centralized(self):
        for q in (10,100,):
            for n in (1,2,10,100,):
                for wf in (100,1000,):
                    self.assertCorrectCentralized( n, q, wf )

if __name__ == '__main__':
    from netuse.sim_utils import OwnArgumentParser
    parser = OwnArgumentParser('Activity test')
    parser.parse_args() # do nothing with the args (already done)
    
    # before you pas control to unittest code, so that the latter code doesn't try to interpret your command line options again when you've already dealt with them
    del sys.argv[1:]
    unittest.main()