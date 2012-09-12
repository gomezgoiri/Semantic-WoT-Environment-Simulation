'''
Created on Dec 31, 2011

@author: tulvur
'''
import os
from rdflib import URIRef
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization

# TODO delete from calculateExpectedResults
def getStationNames(semanticPath):
    def detectOddFiles(list):
        k = {}
        for e in list:
            if not k.has_key(e):
                k[e] = 0
            k[e] += 1
        
        for e in k:
            if k[e]==1:
                print e
    
    ret = []
    dirList=os.listdir(semanticPath+'/dataset')
    for fname in dirList:
        if not fname.startswith("."): # ignore non visible file names
            ret.append( fname.partition("_")[0] )
        
    # detectOddFiles(ret)
    
    return set(ret)

def createDefault():
    es = ExecutionSet()
    
    for strategy in (Parametrization.negative_broadcasting, Parametrization.centralized):
        for numNodes in (2, 5, 10):
            params = Parametrization(strategy=strategy,
                                     amountOfQueries = 100,
                                     writeFrequency = 1000,
                                     nodes = [ "node"+str(i) for i in range(numNodes) ],
                                     simulateUntil = 60000,
                                     queries = ((None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_SnowDepth")),))
            params.save()
            
            execution = Execution(parameters=params)
            execution.save()
            
            es.addExecution(execution)
    
    es.save()





if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create parameters needed for a new.')
    parser.add_argument('-ds','--data-set',
                        default='../../../files/semantic',
                        dest='dataset_path',
                        help='Specify the folder containing the dataset to perform the simulation.')
    parser.add_argument('-se','--subexperiment', default='networkOverload', dest='subexperiment',
            help='Specify which experiment you want to use.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    
    if args.subexperiment=='networkOverload':    
        from netuse.main.subexperiments.networkOverload import parametrize
    if args.subexperiment=='responseTime':
        from netuse.main.subexperiments.responseTime import parametrize
        
    parametrize(semanticPath)