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

import time
import json

class VersionFactory:
    
    def __init__(self, previous_version=None, generation=None):
        if generation is None:
            self.generation = time.time()
        self.previous_version = None
            
    def create_version(self): # TODO remove race conditions
        if self.previous_version is None:
            self.previous_version = Version(self.generation)
        else:
            self.previous_version = Version(self.generation, self.previous_version.version+1)
        return self.previous_version
            

class Version:
    
    def __init__(self, generation, version=0):
        self.generation = generation
        self.version = version
        
    def __cmp__(self, other):
        if self.generation is other.generation:
            return self.version - other.version
        return self.generation - other.generation
    
    def to_json(self):
        dictio = {'g': self.generation, 'v': self.version}
        return json.dumps(dictio)
    
    @staticmethod
    def create_from_json(json_str):
        dictio = json.loads(json_str)
        return Version( dictio['g'], dictio['v'] )