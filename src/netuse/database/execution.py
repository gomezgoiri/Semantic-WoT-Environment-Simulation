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

import datetime
from mongoengine import Document, DateTimeField, ListField, StringField, ReferenceField
from mongoengine.queryset import QuerySet
from netuse.database.parametrization import Parametrization

class Execution(Document):
    meta = {'collection': 'executions'}
    
    # executions are repeated if they have exactly the same "parameters" attribute
    parameters = ReferenceField(Parametrization) 
    execution_date = DateTimeField(default=None) # when this was started being simulated?
    #requests = ListField(ReferenceField(HTTPTrace))
# db.eval(function(){return db.executions.find().map(function (obj) { return obj.requests.length });})

class AwesomerQuerySet(QuerySet):
    
    def AwesomerQuerySet(self):
        super(AwesomerQuerySet, self).__init__()
    
    def get_simulated(self):
        #queryset.filter(execution_date__ne=None)
        for es in self:
            all_simulated = True 
            for ex in es.executions:
                if ex.execution_date is None:
                    all_simulated = False
                    break
            if all_simulated:
                yield es
    
    def get_unsimulated(self):
        #queryset.filter(execution_date__ne=None)
        for es in self:
            some_unsimulated = False 
            for ex in es.executions:
                if ex.execution_date is None:
                    some_unsimulated = True
                    break
            if some_unsimulated:
                yield es


class ExecutionSet(Document):
    
    meta = {
            'collection': 'executionSet',
            'ordering': ['-creation_date'], # latest first
            'queryset_class': AwesomerQuerySet
            }
    
    # to identify the experiment
    experiment_id = StringField(default='default')
    creation_date = DateTimeField(default=datetime.datetime.now)
    
    # more than one execution with the same parametrization can be stored
    # to average the results for an specific parametrization
    executions = ListField(ReferenceField(Execution))
    
    def addExecution(self, execution):
        self.executions.append(execution)