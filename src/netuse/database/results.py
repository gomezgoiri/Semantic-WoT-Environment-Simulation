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