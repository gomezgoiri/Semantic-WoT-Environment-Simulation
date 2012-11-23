'''
Created on Nov 23, 2012

@author: tulvur
'''
import time

class VersionFactory:
    
    def __init__(self, generation=None):
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