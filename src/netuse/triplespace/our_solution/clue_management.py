def compare_expiry(tuple_a, tuple_b):
        return cmp(int(tuple_a[0]), int(tuple_b[0])) # compare as integers


class ClueStore(object):
    
    def __init__(self):
        self.bynode = {}
        self.byexpirytime = []  # from shortest to longest
                                # (using a list of tuples instead of dictionary to allow expiry_type repetitions)
        self.started = False
        
    def add_clue(self, expiry_time, node, clue):
        self.started = True
        self.bynode[node] = clue
        self.byexpirytime.append( (expiry_time, node, clue) )
        self.byexpirytime = sorted(self.byexpirytime, compare_expiry)
        
    # TODO remove clues when they have expired
    #      particularly if I'm a whitepage
    
    
    # return the nodes which may have relevant data for a given query
    def get_query_candidates(self, template):
        pass