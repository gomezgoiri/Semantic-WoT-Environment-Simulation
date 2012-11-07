'''
Created on Nov 26, 2011

@author: tulvur
'''
import datetime

# "SimulationTrace" instead of "Simulation" to debug
from SimPy.Simulation import initialize, simulate
from netuse.activity import ActivityGenerator
from netuse.nodes import NodeGenerator
from netuse.database.execution import ExecutionSet, Execution
from netuse.results import G
from netuse.evaluation.utils import ParametrizationUtils

from multiprocessing import Process, Queue, cpu_count


def performSimulation(execution, preloadedGraph={}):
    print "New simulation: %s"%(execution.parameters)
    
    ParametrizationUtils.loadGraphsJustOnce(execution.parameters.nodes, G.dataset_path, preloadedGraph)
    
    initialize()
    G.setNewExecution(execution)
    
    nodes = NodeGenerator(execution.parameters)
    nodes.generateNodes()
    
    activity = ActivityGenerator(execution.parameters, preloadedGraph)
    activity.generateActivity()
    
    # activate
    cool_down = 500
    simulate(until=execution.parameters.simulateUntil+cool_down)
    
    G.shutdown()

            
class SimulationPerformer(Process):
    
    def __init__(self, name=None, queue=None):
        Process.__init__(self, name=name)
        self.execution_ids = queue
    
    def mark_execution(self, execution):
        ''' This method is used to warn another processes that this one is already processing it.'''
        execution.execution_date = datetime.datetime.now()
        execution.save()
    
    def run(self):
        while not self.execution_ids.empty():
            execution_id = self.execution_ids.get() # race condition between while and this sentence
            ex = Execution.objects(id=execution_id).first()
            if ex.execution_date==None and ex.parameters!=None: # race condition in the mongodb update between processes in different machines
                self.mark_execution(ex) # 2 processes in different processes (or machines)
                performSimulation(ex)

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