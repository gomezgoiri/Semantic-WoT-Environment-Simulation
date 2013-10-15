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

from mongoengine import Document, ListField, StringField

# class to preload Gossipings
class Gossipings(Document):
    meta = {'collection': 'gossipings'}
    
    node = StringField()
    gossips = ListField(StringField(), default=list) 
    gossips_expanded = ListField(StringField(), default=list)