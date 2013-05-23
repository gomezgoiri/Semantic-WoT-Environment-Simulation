'''
Created on May 23, 2013

@author: tulvur
'''

class QueryCacher(object):

    def __init__(self):
        self.positive_answers = {} # dict of set()
        self.negative_answers = {} # dict of set()
    
    def get_relevant_nodes(self, template, all_nodes):
        '''Returns the following nodes:
             * Nodes which have answered to this query in the past
             * Nodes that have not answered to this query in the past
        '''
        relevant = set()
        if template not in self.negative_answers:
            return set(all_nodes) # no matter if they are positive or unknown
        
        for node in all_nodes:
            node_name = str(node)
            if template in self.positive_answers and node_name in self.positive_answers[template]:
                relevant.add(node)
            elif template in self.negative_answers and node_name not in self.negative_answers[template]:
                relevant.add(node)
        return relevant 
    
    def cache(self, template, node, response):
        node_name = str(node)
        
        if response.getstatus() == 200:
            if template in self.negative_answers:
                if node_name in self.negative_answers[template]: # not possible, but anyway...
                    self.negative_answers[template].remove(node_name)
            
            if template not in self.positive_answers:
                self.positive_answers[template] = set()
            self.positive_answers[template].add(node_name)
             
        elif response.getstatus() == 404:
            if template in self.positive_answers:
                if node_name in self.positive_answers[template]:
                    self.positive_answers[template].remove(node_name)
                
            if template not in self.negative_answers:
                self.negative_answers[template] = set()
            self.negative_answers[template].add(node_name)
             
        # other status are ignored: the previous state of the node in the cache is maintained