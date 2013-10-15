# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

from bson.objectid import ObjectId
from netuse.database.execution import ExecutionSet
from netuse.database.results import HTTPTrace
from netuse.database.parametrization import Parametrization

def delete(executionSets):
    for es in executionSets:
        for ex in es.executions:
            for req in HTTPTrace.objects(execution=ex.id):
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