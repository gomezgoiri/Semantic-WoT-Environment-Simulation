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
from netuse.database.parametrization import Parametrization
from netuse.database.execution import ExecutionSet

def search_execution(execution_set, strategy, num_nodes, num_consumers):
    for ex in execution_set.executions:
        params = ex.parameters
        if params.strategy==strategy and len(params.nodes)==num_nodes and params.numConsumers==num_consumers:
            print ex.id


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage data.')
    parser.add_argument('-o','--oid', default=None, dest='oid',
                help='Specify the object id of the execution set to be looked for into. Otherwise the last execution set should be selected.')
    parser.add_argument('-s','--strategy', default=Parametrization.our_solution, dest='strategy',
                help='The strategy the searched execution should have.')
    parser.add_argument('-N','--num_nodes', type=int, default=100, dest='num_nodes',
                help='The number of nodes the searched execution should have.')
    parser.add_argument('-Nc','--num_consumers', type=int, default=100, dest='num_consumers',
                help='The number of consumer nodes the searched execution should have.')
    
    args = parser.parse_args()
    objID = args.oid
    
    if objID==None:
        search_execution(ExecutionSet.objects.first(), args.strategy, args.num_nodes, args.num_consumers)
    else:
        search_execution(ExecutionSet.objects(id=ObjectId(objID)).first(), args.strategy, args.num_nodes, args.num_consumers)


if __name__ == '__main__':
    main()