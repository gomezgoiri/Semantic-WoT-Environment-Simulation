'''
Created on Feb 18, 2012

@author: tulvur
'''
from mongoengine import Document, ListField, StringField

# class to preload Gossipings
class Gossipings(Document):
    meta = {'collection': 'gossipings'}
    
    node = StringField()
    gossips = ListField(StringField(), default=list) 
    gossips_expanded = ListField(StringField(), default=list)