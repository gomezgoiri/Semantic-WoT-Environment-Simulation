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

from mongoengine import Document, StringField, BooleanField
import pickle

class RequestsResults(Document):
    meta = {'collection': 'expected'}
    
    station_name = StringField() # name of the station (node)
    has_result = BooleanField(default=False)
    
    _query = StringField(required=True, default=pickle.dumps(('*', '*', '*',)))
    #queries = property(getQueries, setQueries, None, "queries!")
    @property
    def query(self):
        return pickle.loads( str(self._query) )
        
    @query.setter
    def query(self, q):
        self._query = pickle.dumps( q )
    
    @query.deleter
    def query(self):
        del self._query