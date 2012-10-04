'''
Created on Nov 27, 2011

@author: tulvur
'''
from netuse.database.execution import Execution
from mongoengine import Document, StringField, FloatField, IntField, ReferenceField

class NetworkTrace(Document):
    meta = {'collection': 'net_trace',
            'indexes': ['execution',],
    }
    
    execution = ReferenceField(Execution)
    timestamp = FloatField(default=0.0)
    client = StringField()
    server = StringField()
    path = StringField()
    status = IntField(default=0)
    response_time = FloatField(default=0.0)
    
    # Possible extensions
    #  + bandwidth (or data exchanged)
    #  + path = StringField()
    
    

class RequestsResults(Document):
    meta = {'collection': 'results'}
    
    found = IntField(default=0)
    not_found = IntField(default=0)
    server_error = IntField(default=0)
    timeout = IntField(default=0)
    success = IntField(default=0)
    failure = IntField(default=0)
    total = IntField(default=0)

class Results(Document):
    meta = {'collection': 'results'}
    
    requests = ReferenceField(RequestsResults)
    response_time_mean = FloatField(default=0.0)
    data_exchanged = FloatField(default=0.0)


# A medir:
#    numero de comunicaciones necesarias / producidas (eficiencia)
#    tiempo medio en el que cada nodo ha estado ocupado
#    tiempo necesario para obtener respuesta
#    cuando sporadic pasa a ser continuous? (dependiendo de las var indep)