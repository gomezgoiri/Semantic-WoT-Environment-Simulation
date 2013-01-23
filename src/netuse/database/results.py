'''
Created on Nov 27, 2011

@author: tulvur
'''
from netuse.database.execution import Execution
from mongoengine import Document, StringField, FloatField, IntField, ReferenceField, DictField, ListField, NULLIFY

class HTTPTrace(Document):
    meta = {'collection': 'http_trace',
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


class UDPTrace(Document):
    meta = {'collection': 'udp_trace',
            'allow_inheritance': True,
            'indexes': ['execution',],
    }
    
    execution = ReferenceField(Execution)
    timestamp = FloatField(default=0.0)
    fromm = StringField( required = True )
    
class MDNSSubQuery(Document):
    meta = {'collection': 'udp_trace'}
    name = StringField( required = True )
    # right now just these types
    record_type = StringField( required = True, default = "PTR", choices = ( "PTR", "SVR", "TXT" ) )
    
class MDNSRecord(Document):
    meta = {'collection': 'udp_trace',
            'allow_inheritance': True}
    name = StringField( required = True ) # instance name or service name (e.g. query PTR)
    ttl = IntField( default=0 ) # remember that ttl is measured in seconds and simulation time in ms!

class PTRRecord(MDNSRecord):
    type = "PTR" # don't want to store this
    domain_name = StringField( required = True )

class TXTRecord(MDNSRecord):
    type = "TXT" # don't want to store this
    keyvalues = DictField( required = True )

class SVRRecord(MDNSRecord):
    type = "SVR" # don't want to store this
    hostname = StringField( required = True )
    port = IntField( default=0 )

class MDNSQueryTrace(UDPTrace):
    # "execution" and "indexed" inherited
    question_type = StringField( required = True, default = "QM", choices = ( "QM", "QU" ) )
    queries = ListField(ReferenceField(MDNSSubQuery, reverse_delete_rule=NULLIFY), required=True)
    known_answers = ListField(ReferenceField(MDNSRecord, reverse_delete_rule=NULLIFY), required=False) # it can be empty

class MDNSAnswerTrace(UDPTrace):
    # "execution" and "indexed" inherited
    answers = ListField(ReferenceField(MDNSRecord, reverse_delete_rule=NULLIFY), required=True)
    to = StringField( required = True, default = "all" ) # "all" (multicast) or the name of the node (unicast)