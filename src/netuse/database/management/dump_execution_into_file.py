'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.tracers import FileTracer
from netuse.database.results import NetworkTrace


def dump_into_file(execution_id, file_path):
    ft = FileTracer(file_path)
    ft.start()
    
    for req in NetworkTrace.objects(execution=execution_id):
        ft.trace(req.timestamp, req.client, req.server, req.path, req.status, req.response_time)
    ft.stop()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be used.')
    parser.add_argument('-p','--path', default='/tmp/trace.txt', dest='file_path',
                help='Specify the path of the file where the trace is going to be written.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID==None:
        raise Exception("A oid should be provided.")
    else:
        dump_into_file(ObjectId(objID), args.file_path)


if __name__ == '__main__':
    main()