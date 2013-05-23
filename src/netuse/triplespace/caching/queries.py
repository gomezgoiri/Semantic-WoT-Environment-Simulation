'''
Created on May 23, 2013

@author: tulvur
'''

class QueryCacher(object):

    def __init__(self):
        self.positive_answers = set()
        self.negative_answers = set()
    
    def get_relevant_nodes(self, all_nodes):
        '''Returns the following nodes:
             * Nodes which have answered to this query in the past
             * Nodes that have not answered to this query in the past
        '''
        relevant = set()
        for node in all_nodes:
            node_name = str(node)
            if node_name in self.positive_answers:
                relevant.add(node)
            elif node_name not in self.negative_answers:
                relevant.add(node)
        return relevant 
    
    def cache(self, node, response):
        node_name = str(node)
        
        if response.getstatus() == 200:
            if node_name in self.negative_answers: # not possible, but anyway...
                self.negative_answers.remove(node_name)
            self.positive_answers.add(node_name)
             
        elif response.getstatus() == 404:
            if node_name in self.positive_answers:
                self.positive_answers.remove(node_name)
            self.negative_answers.add(node_name)
             
        # other status are ignored: the previous state of the node in the cache is maintained