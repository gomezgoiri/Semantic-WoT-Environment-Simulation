
from clueseval.clues.predicate_based import PredicateBasedClue

class ClueManager:
    '''
    This class mantains a cache of the selected clue.
    '''
    
    def __init__(self, dataaccess):
        self.dataaccess = dataaccess
        self.cached_clue = None
        self.refresh()
        
    def refresh(self):
        g = self.dataaccess.getSpace(None)
        clue = PredicateBasedClue()
        clue.parseGraph(g)
        
        if clue!=self.cached_clue:
            self.cached_clue = clue
            
    def get_clue(self):
        return self.cached_clue