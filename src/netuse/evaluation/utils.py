'''
Created on Dec 31, 2011

@author: tulvur
'''
import os
import random
from rdflib import URIRef, RDF
from netuse.devices import RegularComputer
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization


class ParametrizationUtils():
    
    def __init__(self, experiment_id, semanticPath, repetitions=1):
        self.possibleNodes = ParametrizationUtils.getStationNames(semanticPath)
        self.es = ExecutionSet(experiment_id=experiment_id) # 'network_use'
        self.repetitions = repetitions
        
    def createDefaultParametrization(self, strategy, amountOfQueries, writeFrequency, simulateUntil, queries, numNodes, nodeTypes=None):
        nodes = random.sample(self.possibleNodes, numNodes)
        
        params = Parametrization(strategy = strategy,
                        amountOfQueries = amountOfQueries,
                        writeFrequency = writeFrequency,
                        nodes = nodes,
                        nodeTypes = nodeTypes if nodeTypes!=None else (RegularComputer.TYPE_ID,)*numNodes,
                        simulateUntil = simulateUntil,
                        queries = ((None, RDF.type, URIRef('http://knoesis.wright.edu/ssw/ont/weather.owl#RainfallObservation')),
                                    (URIRef('http://dev.morelab.deusto.es/bizkaisense/resource/station/ABANTO'), None, None)
                                    ,)
                        )
        params.save()
        self._repeatExperiment(params)
        
    def _repeatExperiment(self, params):
        '''Repeating each experiment's execution, we increase the accuracy of the obtained data.'''
        for _ in range(self.repetitions):
            execution = Execution(parameters=params)
            self.es.addExecution(execution)
            execution.save() # self.es is automatically saved too (see execution's save method)
        self.es.save()

    # TODO delete from calculateExpectedResults
    # TODO using among different projects (e.g. clueseval)
    @staticmethod
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