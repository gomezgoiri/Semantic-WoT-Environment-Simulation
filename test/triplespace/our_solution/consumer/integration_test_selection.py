from SimPy.Simulation import initialize, simulate

from netuse.results import G, FileTracer
from netuse.nodes import NodeGenerator
from netuse.activity import ActivityGenerator
from netuse.evaluation.utils import ParametrizationUtils
from netuse.database.parametrization import Parametrization

# This script generates a simulation and records its trace in a file.
# Used to check the functionalities under really simple simulation conditions.

def performSimulation(parameters):    
    initialize()
    G.setNewExecution(None, tracer=FileTracer('/tmp/trace.txt'))
    
    nodes = NodeGenerator(parameters)
    nodes.generateNodes()
    
    activity = ActivityGenerator(parameters, None)
    activity.generateActivity()
    
    # activate
    cool_down = 500
    simulate(until=parameters.simulateUntil+cool_down)
    
    G.shutdown()


if __name__ == '__main__':
    p = ParametrizationUtils('network_usage', '/home/tulvur/dev/workspaces/doctorado/files/semantic')
    
    param = p.getDefaultParametrization(Parametrization.our_solution,
                                   amountOfQueries = 1,
                                   writeFrequency = 10000,
                                   simulateUntil = 60000,
                                   queries = ((None, None, None),),
                                   numNodes = 2,
                                   numConsumers = 1
                                   )
    performSimulation(param)