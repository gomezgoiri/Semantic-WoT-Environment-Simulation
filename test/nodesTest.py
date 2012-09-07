'''
Created on Nov 28, 2011

@author: tulvur
'''

import unittest
from rdflib import URIRef
from SimPy.SimulationTrace import *
from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.parametrization import Parametrization
from netuse.results import G
from netuse.main.simulate import loadGraphsJustOnce

PREFIXES = {
            'om-owl': 'http://knoesis.wright.edu/ssw/ont/sensor-observation.owl#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'sens-obs': 'http://knoesis.wright.edu/ssw/',
            'owl-time': 'http://www.w3.org/2006/time#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'weather': 'http://knoesis.wright.edu/ssw/ont/weather.owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
            }

semanticPath = '../files/semantic'

class TestNodes(unittest.TestCase):
    
    def setUp(self):
        G.Rnd = random.Random(12346)
    
    def performSimulation(self, parameters, extraActivityGenerator):
        trace.tchange(outfile=open(r"/tmp/simulation.log","w"))
        trace.ttext("New simulation!")
        initialize()
        G.newExecution()
        
        self.nodes = NodeGenerator(parameters)
        self.nodes.generateNodes()
        
        preloadedGraphs = loadGraphsJustOnce(parameters.nodes, semanticPath)
        activity = ActivityGenerator(parameters, preloadedGraphs)
        activity.generateActivity()
        
        extraActivityGenerator()
        
        #stats = Stats(parameters, nodes)
        simulate(until=parameters.simulateUntil*1.5)
        
    def testCheckSpectedResponses(self):
        def generateActivityFromNode0():
            actionNode = NodeGenerator.getNodes()[0]
            actionNode.ts.setLogRequests(True)
            actionNode.ts.query((None, URIRef(PREFIXES['om-owl']+'observedProperty'), None), startAt=20) # all nodes affected
            actionNode.ts.query((URIRef(PREFIXES['sens-obs']+'System_KHTO'), None, None), startAt=40) # just KHTO affected
            actionNode.ts.query((URIRef(PREFIXES['sens-obs']+'System_KBTL'), None, None), startAt=60) # just KBTL affected
            actionNode.ts.query((URIRef(PREFIXES['sens-obs']+'System_AAAA'), None, None), startAt=80) # none affected

        param = Parametrization(strategy=Parametrization.negative_broadcasting,
                                 amountOfQueries=0, # to force the queries from a known node
                                 writeFrequency=50,
                                 nodes = ('KHTO', 'KBTL', 'AAAA'),
                                 simulateUntil = 150)
        
        self.performSimulation(param, generateActivityFromNode0)
        self._testReceivedResponses(0, ((200, 2),))
        self._testReceivedResponses(1, ((200, 1),(404, 1)))
        self._testReceivedResponses(2, ((200, 1),(404, 1)))
        self._testReceivedResponses(3, ((404, 2),))
        
        
    def _testReceivedResponses(self, reqNum, codes):
        actionNode = NodeGenerator.getNodes()[0]
        for c in codes:
            code = c[0]
            numberoftimes = c[1]
            
            count = 0
            for r in actionNode.ts.requests[reqNum].responses:
                if r.getstatus()==code:
                    count += 1
            
            self.assertEquals(numberoftimes, count)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Start simulation process.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    
    # before you pas control to unittest code, so that the latter code doesn't try to interpret your command line options again when you've already dealt with them
    del sys.argv[1:]
    unittest.main()