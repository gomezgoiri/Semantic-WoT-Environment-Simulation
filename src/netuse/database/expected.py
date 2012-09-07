'''
Created on Jan 8, 2012

@author: tulvur
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