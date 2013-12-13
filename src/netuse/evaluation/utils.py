# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''
import random
from matplotlib.ticker import FuncFormatter
from netuse.devices import RegularComputer
from netuse.database.execution import ExecutionSet, Execution
from netuse.database.parametrization import Parametrization
from commons.utils import SemanticFilesLoader

class Parameters():
    def __init__(self, simulateUntil=None, discovery=None, strategy=None, network_model=None, amountOfQueries=None,
                 writeFrequency=None, queries=None, nodes=None, numConsumers=None, nodeTypes=None):
        self.simulateUntil = simulateUntil
        self.discovery = discovery
        self.strategy = strategy
        self.network_model = network_model
        self.amountOfQueries = amountOfQueries
        self.writeFrequency = writeFrequency
        self.queries = queries
        self.nodes = nodes
        self.numConsumers = numConsumers
        self.nodeTypes = nodeTypes
    
    def fill_blank_values(self, default_values): # default_values is an instance of Parameters also, with some default values )
        filled_copy = Parameters(
                            simulateUntil = self.simulateUntil,
                            discovery = self.discovery,
                            strategy = self.strategy,
                            amountOfQueries = self.amountOfQueries,
                            writeFrequency = self.writeFrequency,
                            queries = self.queries,
                            nodes = self.nodes,
                            numConsumers = self.numConsumers,
                            nodeTypes = self.nodeTypes,
                            network_model = self.network_model
                        )
        
        if filled_copy.simulateUntil is None: filled_copy.simulateUntil = default_values.simulateUntil
        if filled_copy.discovery is None: filled_copy.discovery = default_values.discovery
        if filled_copy.strategy is None: filled_copy.strategy = default_values.strategy
        if filled_copy.network_model is None: filled_copy.network_model = default_values.network_model
        if filled_copy.amountOfQueries is None: filled_copy.amountOfQueries = default_values.amountOfQueries
        if filled_copy.writeFrequency is None: filled_copy.writeFrequency = default_values.writeFrequency
        if filled_copy.queries is None: filled_copy.queries = default_values.queries
        if filled_copy.nodes is None: filled_copy.nodes = default_values.nodes
        if filled_copy.numConsumers is None: filled_copy.numConsumers = default_values.numConsumers
        if filled_copy.nodeTypes is None: filled_copy.nodeTypes = default_values.nodeTypes
        
        return filled_copy


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
                    discovery = parameters.discovery,
                    strategy = parameters.strategy,
                    network_model = parameters.network_model,
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
                    filled_params = var_params.fill_blank_values(self.default_parameters)
                    filled_params.nodes = nodes
                    
                    try:
                        params = self.create_parametrization(filled_params)
                        params.save()
                        
                        execution = Execution(parameters=params)
                        execution.save()
                    
                        self.es.addExecution(execution)
                    except Exception as e:
                        print e
        self.es.save() # save just once with all the executions


def millions_format(x, pos):
    '100000000 => 100.000.000'
    if x==0: return "0" # without commas!
    if x<1000:
        return x
    thousand_units, remaining_units = x/1000, x%1000
    if x<1000000:
        return "%d.%03d" % (thousand_units, remaining_units)
    return "%d.%03d.%03d" % (thousand_units/1000, thousand_units%1000, remaining_units)

millions_formatter = FuncFormatter(millions_format)
