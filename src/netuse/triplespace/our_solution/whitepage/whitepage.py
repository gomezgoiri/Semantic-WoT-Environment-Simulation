from netuse.triplespace.our_solution.clue_management import ClueStore

class Whitepage(object):
    
    def __init__(self):
        self.clues = ClueStore()
        
    def get_query_candidates(self, template):
        self.clues.get_query_candidates(template)
    
    def add_clue(self, node, clue, expiry_time=-1):
        self.clues.add_clue(node, clue, expiry_time)
        
    def get_aggregated_clues_json(self):
        self.clues.get_aggregated_clues_json()