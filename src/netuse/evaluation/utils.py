'''
Created on Dec 31, 2011

@author: tulvur
'''
import random
from netuse.devices import RegularComputer
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization
from commons.utils import SemanticFilesLoader

class Parameters():
    def __init__(self, simulateUntil=None, strategy=None, amountOfQueries=None, writeFrequency=None,
                 queries=None, nodes=None, numConsumers=None, nodeTypes=None):
        self.simulateUntil = simulateUntil
        self.strategy = strategy
        self.amountOfQueries = amountOfQueries
        self.writeFrequency = writeFrequency
        self.queries = queries
        self.nodes = nodes
        self.numConsumers = numConsumers
        self.nodeTypes = nodeTypes
    
    def fill_blank_values(self, default_values): # default_values is an instance of Parameters also, with some default values )
        if self.simulateUntil is None: self.simulateUntil = default_values.simulateUntil
        if self.strategy is None: self.strategy = default_values.strategy
        if self.amountOfQueries is None: self.amountOfQueries = default_values.amountOfQueries
        if self.writeFrequency is None: self.writeFrequency = default_values.writeFrequency
        if self.queries is None: self.queries = default_values.queries
        if self.nodes is None: self.nodes = default_values.nodes
        if self.numConsumers is None: self.numConsumers = default_values.numConsumers
        if self.nodeTypes is None: self.nodeTypes = default_values.nodeTypes


class ParametrizationUtils():
    
    def __init__(self, experiment_id, semanticPath, default_parameters, repetitions=1): # possible constants
        self.es = ExecutionSet(experiment_id=experiment_id) # 'network_use'
        self.default_parameters = default_parameters
        self.repetitions = repetitions
        
        sfl = SemanticFilesLoader(semanticPath)
        self.possibleNodes = sfl.getStationNames()
    
    def create_parametrization(self, parameters):
        if len(parameters.nodes) < parameters.numConsumers:
            raise Exception('Parametrization error: more consumers (%d) than nodes (%d) in the simulation.'%(parameters.numConsumers, len(parameters.nodes)))
        
        if parameters.nodeTypes is None:
            parameters.nodeTypes = (RegularComputer.TYPE_ID,)*len(parameters.nodes)
        
        return Parametrization (
                    strategy = parameters.strategy,
                    amountOfQueries = parameters.amountOfQueries,
                    numConsumers = parameters.numConsumers,
                    writeFrequency = parameters.writeFrequency,
                    nodes = parameters.nodes,
                    nodeTypes = parameters.nodeTypes,
                    simulateUntil = parameters.simulateUntil,
                    queries = parameters.queries
                )
    
    def get_random_nodes(self, network_size):
        if network_size<=len(self.possibleNodes):
            return random.sample(self.possibleNodes, network_size)
        else:
            nodes = list(self.possibleNodes) # copies the list (or more cryptic: self.possibleNodes[:])
            for i in range(network_size-len(self.possibleNodes)):
                nodes.append("DOE_%d"%(i))
            return nodes
    
    def save_repeating(self, network_size=None, rest_variable_parameters=()):
        '''Repeating each experiment's execution, we increase the statistical power of the data obtained.'''
        self.save_repeating_for_network_sizes( (network_size,), rest_variable_parameters )
    
    def save_repeating_for_network_sizes(self, network_sizes=(), rest_variable_parameters=()):
        '''Repeating each experiment's execution, we increase the statistical power of the data obtained.'''
        for _ in range(self.repetitions):
            for nsize in network_sizes:            
                nodes = self.get_random_nodes(nsize) # different nodes for different repetition
                
                for var_params in rest_variable_parameters:
                    var_params.nodes = nodes
                    var_params.fill_blank_values(self.default_parameters)
                    
                    try:
                        params = self.create_parametrization(var_params)
                        params.save()
                        
                        execution = Execution(parameters=params)
                        execution.save()
                    
                        self.es.addExecution(execution)
                    except Exception as e:
                        print e
        self.es.save() # save just once with all the executions