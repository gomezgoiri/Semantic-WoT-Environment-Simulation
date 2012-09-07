'''
Created on Jan 7, 2012

@author: tulvur
'''
from pymongo.objectid import ObjectId
from netuse.database.execution import ExecutionSet

def delete(executionSets):
    for es in executionSets:
        for ex in es.executions:
            if ex.parameters!=None:
                ex.parameters.delete()
            if ex.results!=None:
                if ex.results.requests!=None:
                    ex.results.requests.delete()
                ex.results.delete()
            ex.delete()
        es.delete()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-d','--delete', default='unsimulated', dest='delete',
                help='Specify the object id of the execution set to be destroyed. Otherwise the unsimulated ones will be destroyed.')
    
    args = parser.parse_args()
    objID = args.delete
    
    if objID=='unsimulated':
        delete(ExecutionSet.get_unsimulated)
    else:
        delete(ExecutionSet.objects(id=ObjectId(objID)))