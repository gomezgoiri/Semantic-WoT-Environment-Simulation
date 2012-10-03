
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
        '''
        Checks in the data access layer if the clue needs to be updated.
        If the clue is updated, it returns True.
        '''
        g = self.dataaccess.getSpace(None).graphs
        clue = PredicateBasedClue()
        clue.parseGraph(g)
        
        if clue!=self.cached_clue:
            self.cached_clue = clue
            return True
        return False
            
    def get_clue(self):
        return self.cached_clue