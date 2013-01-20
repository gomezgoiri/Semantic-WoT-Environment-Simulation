from clueseval.clues.storage.sqlite import SQLiteClueStore

class Whitepage(object):
    
    def __init__(self, clue_store, generation_time = None):
        if clue_store is None:
            self.clues = SQLiteClueStore(generation_time, in_memory=True) # generation time == 0, this should change
            self.clues.start() # TODO when should be stopped???
        else:
            self.clues = clue_store
        
    def get_query_candidates(self, template):
        return self.clues.get_query_candidates(template)
    
    def add_clue(self, node, clue_json):
        # TODO a wrapper to remove clues when they expire
        self.clues.add_clue(node, clue_json)
        
    def get_aggregated_clues_json(self):
        return self.clues.toJson()