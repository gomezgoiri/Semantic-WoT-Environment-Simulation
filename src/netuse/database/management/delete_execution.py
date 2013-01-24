'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.database.execution import Execution
from netuse.database.results import HTTPTrace

def reset_execution(execution_id):    
    for req in HTTPTrace.objects(execution=execution_id):
        req.delete()
    
    ex = Execution.objects(id=execution_id).first()
    ex.execution_date = None
    ex.save()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be destroyed.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID==None:
        raise Exception("A oid should be provided.")
    else:
        reset_execution(ObjectId(objID))


if __name__ == '__main__':
    main()