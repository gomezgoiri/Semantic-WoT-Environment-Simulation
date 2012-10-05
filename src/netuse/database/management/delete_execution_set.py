'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.database.execution import ExecutionSet
from netuse.database.results import NetworkTrace
from netuse.database.parametrization import Parametrization

def delete(executionSets):
    for es in executionSets:
        for ex in es.executions:
            for req in NetworkTrace.objects(execution=ex.id):
                req.delete()
            params = Parametrization.objects(id=ObjectId(ex.parameters.id)).first()
            if params!=None:
                params.delete()
            ex.delete()
        es.delete()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be destroyed. Otherwise the unsimulated ones will be destroyed.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID is None:
        delete(ExecutionSet.objects.get_unsimulated())
    else:
        delete(ExecutionSet.objects(id=ObjectId(objID)))

if __name__ == '__main__':
    main()