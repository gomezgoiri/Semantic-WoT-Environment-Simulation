'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.tracers import FileTracer
from netuse.database.execution import Execution


def dump_into_file(execution, file_path):
    ft = FileTracer(file_path)
    ft.start()
    for req in execution.requests:
        ft.trace(req.timestamp, req.client, req.server, req.path, req.status, req.response_time)
    ft.stop()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be used.')
    parser.add_argument('-p','--path', default='/tmp/trace.txt', dest='path',
                help='Specify the path of the file where the trace is going to be written.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID==None:
        raise Exception("A oid should be provided.")
    else:
        dump_into_file(Execution.objects(id=ObjectId(objID)).first())