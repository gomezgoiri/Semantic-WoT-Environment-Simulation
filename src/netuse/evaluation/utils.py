'''
Created on Dec 31, 2011

@author: tulvur
'''
import os
import random
from netuse.devices import RegularComputer
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization


class ParametrizationUtils():
    
    def __init__(self, experiment_id, semanticPath, repetitions=1):
        self.possibleNodes = ParametrizationUtils.getStationNames(semanticPath)
        self.es = ExecutionSet(experiment_id=experiment_id) # 'network_use'
        self.repetitions = repetitions
    
    def getDefaultParametrization(self, strategy, amountOfQueries, writeFrequency, simulateUntil, queries, numNodes, numConsumers, nodeTypes=None):
        if numNodes<numConsumers:
            raise Exception('Parametrization error: more consumers than nodes in the simulation.')
        
        if numNodes<=len(self.possibleNodes):
            nodes = random.sample(self.possibleNodes, numNodes)
        else:
            nodes = list(self.possibleNodes) # copies the list (or more cryptic: self.possibleNodes[:])
            for i in range(numNodes-len(self.possibleNodes)):
                nodes.append("DOE_%d"%(i))
        
        if nodeTypes==None:
            nodeTypes = (RegularComputer.TYPE_ID,)*numNodes
        
        params = Parametrization(strategy = strategy,
                        amountOfQueries = amountOfQueries,
                        numConsumers=numConsumers,
                        writeFrequency = writeFrequency,
                        nodes = nodes,
                        nodeTypes = nodeTypes,
                        simulateUntil = simulateUntil,
                        queries = queries
                        )
        return params
    
    def createDefaultParametrization(self, strategy, amountOfQueries, writeFrequency, simulateUntil, queries, numNodes, numConsumers, nodeTypes=None):
        params = self.getDefaultParametrization(strategy, amountOfQueries, writeFrequency, simulateUntil, queries, numNodes, numConsumers, nodeTypes)
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
    def getStationNames(semanticPath, filter_subfolders=None):        
        ret = set()
        dirList=os.listdir(semanticPath+'/data')
        for folder in dirList:
            if not folder.startswith(".") and ( (filter_subfolders is None) or (folder in filter_subfolders) ) :
                subdirList = os.listdir(semanticPath+'/data/'+folder)
                for fname in subdirList:
                    if not fname.startswith("."): # ignore non visible file names
                        ret.add( fname.partition("_")[0] )
        return ret