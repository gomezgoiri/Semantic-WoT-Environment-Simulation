'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.tracers.http import FileHTTPTracer
from netuse.database.execution import ExecutionSet
from netuse.database.results import NetworkTrace


def dump_into_file(execution_id, file_path=None):
    if file_path is None:
        file_path = "/tmp/trace_%s.txt"%execution_id
    ft = FileHTTPTracer(file_path)
    ft.start()
    
    for req in NetworkTrace.objects(execution=execution_id):
        ft.trace(req.timestamp, req.client, req.server, req.path, req.status, req.response_time)
    ft.stop()

def dump_executions_into_file(executionSet):
    for execution in executionSet.executions:
        dump_into_file(execution.id) # ObjectId(objID)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    group = parser.add_mutually_exclusive_group()
    ex_group = group.add_argument_group('execution', 'Dump of a specific execution.')
    ex_group.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution to be used.')
    ex_group.add_argument('-p','--path', default='/tmp/trace.txt', dest='file_path',
                help='Specify the path of the file where the trace is going to be written.')
    group.add_argument('-a','--all', default=None, dest='all',
                help='Specify the object id of the execution set to be used. If no oid is provided, the last simulated one will be used.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID is None:
        if args.all is None:
            dump_executions_into_file(ExecutionSet.objects(experiment_id='dynamism').first())
        else:
            dump_executions_into_file(ExecutionSet.objects(id=ObjectId(objID)))
        #raise Exception("A oid should be provided.")
    else:
        dump_into_file(ObjectId(objID), args.file_path)


if __name__ == '__main__':
    main()