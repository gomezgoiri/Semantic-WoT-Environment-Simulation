'''
Created on Nov 27, 2011

@author: tulvur
'''
from mongoengine import Document, FloatField, IntField, ReferenceField

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