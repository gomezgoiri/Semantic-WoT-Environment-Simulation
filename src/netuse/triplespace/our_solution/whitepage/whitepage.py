from clueseval.clues.storage.memory import MemoryClueStore

class Whitepage(object):
    
    def __init__(self):
        self.clues = MemoryClueStore()
        
    def get_query_candidates(self, template):
        return self.clues.get_query_candidates(template)
    
    def add_clue(self, node, clue_json):
        # TODO a wrapper to remove clues when they expire
        self.clues.add_clue(node, clue_json)
        
    def get_aggregated_clues_json(self):
        return self.clues.toJson()