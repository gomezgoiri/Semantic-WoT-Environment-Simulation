'''
Created on Jan 7, 2012

@author: tulvur
'''
from bson.objectid import ObjectId
from netuse.database.execution import Execution

def delete(execution):
    for r in execution.requests:
        r.delete()
    execution.execution_date = None
    execution.save()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be destroyed.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID==None:
        raise Exception("A oid should be provided.")
    else:
        delete(Execution.objects(id=ObjectId(objID)).first())