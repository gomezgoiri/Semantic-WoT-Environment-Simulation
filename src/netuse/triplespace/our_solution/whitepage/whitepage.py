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

from clueseval.clues.storage.sqlite import SQLiteClueStore
from clueseval.clues.versions.management import Version

class Whitepage(object):
    
    def __init__(self, generation_time = None):
        self.clues = SQLiteClueStore(generation_time, in_memory=True) # generation time == 0, this should change
        # Initially, if no version is loaded, the version will be the lowest possible
        # This way we force all the providers to send their clues
        # if no version was loaded!
        self.loaded_version = Version(-1, -1)
        self.clues.start()
    
    def stop(self):
        self.clues.stop()
    
    def get_query_candidates(self, template):
        return self.clues.get_query_candidates(template)
    
    def add_clue(self, node, clue_json):
        # TODO a wrapper to remove clues when they expire
        self.clues.add_clue(node, clue_json)
        
    def get_aggregated_clues_json(self):
        return self.clues.toJson()
    
    def initial_data_loading(self, aggregated_clues_json):
        actual_version = self.clues.version # since the version changes on fromJson()
        self.clues.fromJson( aggregated_clues_json )
        self.loaded_version = self.clues.version
        self.clues.set_version( actual_version.generation, actual_version.version )
    
    def get_initially_loaded_version(self):
        return self.loaded_version