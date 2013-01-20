from clueseval.clues.storage.sqlite import SQLiteClueStore

class Whitepage(object):
    
    def __init__(self, generation_time):
        self.clues = SQLiteClueStore(generation_time, in_memory=True)
        self.clues.start() # TODO when should be stopped???
        
    def get_query_candidates(self, template):
        return self.clues.get_query_candidates(template)
    
    def add_clue(self, node, clue_json):
        # TODO a wrapper to remove clues when they expire
        self.clues.add_clue(node, clue_json)
        
    def get_aggregated_clues_json(self):
        return self.clues.toJson()