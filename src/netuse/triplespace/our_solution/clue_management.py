from clueseval.clues.aggregated import ClueAggregation

def compare_expiry(tuple_a, tuple_b):
        return cmp(int(tuple_a[0]), int(tuple_b[0])) # compare as integers


class ClueStore(object):
    
    def __init__(self):
        self.bynode = {}
        self.byexpirytime = []  # from shortest to longest
                                # (using a list of tuples instead of dictionary to allow expiry_type repetitions)
        self.started = False
        
    def add_clue(self, node_name, clue, expiry_time=-1):
        self.started = True
        self.bynode[node_name] = clue
        self.byexpirytime.append( (expiry_time, node_name, clue) )
        self.byexpirytime = sorted(self.byexpirytime, compare_expiry)       
    # TODO remove clues when they have expired
    #      particularly if I'm a whitepage
    
    def add_clues(self, aggregated_clue):
        self.started = True
        # to override the whole bynode attribute: dict([['two', 2], ['one', 1]])
        for node_name, clue in aggregated_clue.clues:
            self.add_clue(node_name, clue)
    
    # return the nodes which may have relevant data for a given query
    def get_query_candidates(self, template):
        candidates = set()
        for node_name, clue in self.bynode.iteritems():
            if clue.isCandidate(template):
                candidates.add(node_name)
        return candidates
        
    def get_aggregated_clues_json(self):
        aggregated = ClueAggregation(self.bynode.iteritems())
        return aggregated.toJson()