'''
Created on Nov 27, 2011

@author: tulvur
'''
import pickle
from mongoengine import Document, StringField, FloatField, IntField, ListField

class Parametrization(Document):
    meta = {'collection': 'parametrization'}
    
    negative_broadcasting = "negative broadcasting"
    centralized = "centralized"
    gossiping = "gossiping"
    
    strategy = StringField(required=True,
                           default=negative_broadcasting)
                           #don't know why stopped working :-S
                           #choices=(negative_broadcasting, centralized, gossiping,))
    simulateUntil = FloatField(required=True, default=60000.0)
    nodes = ListField(StringField(), required=True, default=[])
    nodeTypes = ListField(StringField(), required=True, default=[])
    amountOfQueries = IntField(required=True, default=0)
    numConsumers = IntField(required=True, default=0)
    writeFrequency = IntField(required=True, default=100)
    
    _queries = StringField(required=True, default=pickle.dumps([('*', '*', '*'),]))
    #queries = property(getQueries, setQueries, None, "queries!")
    
    @property
    def queries(self):
        return pickle.loads( str(self._queries) )
    
    @queries.setter
    def queries(self, queries):
        self._queries = pickle.dumps( queries )
    
    @queries.deleter
    def queries(self):
        del self._queries
            
    @property
    def numberOfNodes(self):
        return len(self.nodes)
    
    def __repr__(self):
        return 'Parametrization(strat: %s, nodes: %i, write_freq: %i, #queries: %i)'%(self.strategy, len(self.nodes), self.writeFrequency, self.amountOfQueries)
    
    def __str__(self):
        return self.__repr__()

# Variables independientes:
#    tipos de red: 1-1 pull, 1-* pull sporadic
#    como medir push???
#    tipo de cacharros?
#    escala de la red y/o frecuencia de consulta y frecuencia de escritura?
#    centralizado vs NB vs gossiping sencillo (comparten esquema cada X)