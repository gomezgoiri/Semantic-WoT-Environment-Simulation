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


class Model(Simulation):
    def __init__(self, execution):
        super(Model, self).__init__()
        self.execution = execution
    
    def mark_execution(self):
        ''' This method is used to warn another processes that this one is already processing it.'''
        self.execution.execution_date = datetime.datetime.now()
        self.execution.save()
    
    def runModel(self):
        self.mark_execution() # 2 processes in different processes (or machines)
        
        print "New simulation: %s"%(self.execution.parameters)
        
        sfl = SemanticFilesLoader(G.dataset_path)
        sfl.loadGraphsJustOnce(self.execution.parameters.nodes, preloadedGraph={})
        
        self.initialize()
        G.setNewExecution(self.execution)
        
        nodes = NodeGenerator(self.execution.parameters)
        nodes.generateNodes()
        
        activity = ActivityGenerator(self.execution.parameters, preloadedGraph={})
        activity.generateActivity()
        
        # activate
        cool_down = 500
        self.simulate( until = self.execution.parameters.simulateUntil + cool_down )
        
        G.shutdown()


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