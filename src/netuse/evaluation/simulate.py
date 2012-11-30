'''
Created on Nov 26, 2011

@author: tulvur
'''
import datetime

# "SimulationTrace" instead of "Simulation" to debug
from SimPy.Simulation import Simulation
from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.execution import ExecutionSet, Execution
from netuse.results import G
from commons.utils import SemanticFilesLoader

from multiprocessing import Process, Queue, cpu_count


class BasicModel(Simulation):
    '''
        Network Usage simulation model.
    '''
    
    def __init__(self, parameters, cool_down=500):
        super(BasicModel, self).__init__()
        self.parameters = parameters
        self.cool_down = 500
        self.stoppables = []
    
    def simulate(self, until=0):
        try:
            super(BasicModel, self).simulate( until + self.cool_down )
        finally:
            for stoppable in self.stoppables:
                stoppable.stop()
            G.shutdown()

    def runModel(self):
        pass


class Model(BasicModel):
        
    def __init__(self, execution, cool_down=500):
        super(Model, self).__init__(execution.parameters, cool_down)
        self.execution = execution
        
    def initialize(self):
        G.setNewExecution(self.execution)
        super(Model, self).initialize()
    
    def _mark_execution(self):
        ''' This method is used to warn another processes that this one is already processing it.'''
        self.execution.execution_date = datetime.datetime.now()
        self.execution.save()

    def runModel(self):
        self._mark_execution() # 2 processes in different processes (or machines)
        
        print "New simulation: %s"%(self.parameters)
        
        sfl = SemanticFilesLoader(G.dataset_path)
        sfl.loadGraphsJustOnce(self.parameters.nodes, preloadedGraph={})
        
        self.initialize()
        
        nodes = NodeGenerator(self.parameters, simulation=self)
        nodes.generateNodes()
        self.stoppables.extend( nodes.getNodes() )
        
        activity = ActivityGenerator(self.parameters, preloadedGraph={}, simulation=self)
        activity.generateActivity()
        
        self.simulate( until = self.parameters.simulateUntil )


class SimulationPerformer(Process):
    
    def __init__(self, name=None, queue=None):
        super(SimulationPerformer, self).__init__(name=name)
        self.execution_ids = queue
    
    def run(self):
        while not self.execution_ids.empty():
            execution_id = self.execution_ids.get() # race condition between while and this sentence
            ex = Execution.objects( id=execution_id ).first()
            if ex.execution_date==None and ex.parameters!=None: # race condition in the mongodb update between processes in different machines
                model = Model(ex)
                model.runModel()

def execute_in_n_processors(executionIds_queue, num_processes):
    processes = []
    try:
        for n in range(num_processes):
            sp = SimulationPerformer("Process_%d"%(n), executionIds_queue)
            processes.append(sp)
            sp.start()
    finally:
        for process in processes:
            process.join()

def execute_once_each_time(executionIds_queue):
    execute_in_n_processors(executionIds_queue, 1)

def execute_all_concurrently(executionIds_queue):
    execute_in_n_processors(executionIds_queue, executionIds_queue.qsize())
    
def execute_one_in_each_processor(executionIds_queue):
    execute_in_n_processors(executionIds_queue, cpu_count())


def simulateUnsimulatedExecutionSet():
    one_es_per_execution = True # just one simulation (ExecutionSet) per execution
    
    for es in ExecutionSet.objects.get_unsimulated():
        executionIds_queue = Queue()
        for ex in es.executions:
            executionIds_queue.put(ex.id)
        
        #execute_all_concurrently(executionIds_queue)
        execute_one_in_each_processor(executionIds_queue)
        #execute_once_each_time(executionIds_queue)
        
        if one_es_per_execution:
            break

# Entry point for setup.py
def main():
    from netuse.sim_utils import OwnArgumentParser
    parser = OwnArgumentParser('Start simulation process.')
    parser.parse_args()
    simulateUnsimulatedExecutionSet()
    
if __name__ == '__main__':
    main()