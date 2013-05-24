'''
Created on Aug 17, 2012

@author: tulvur
'''
#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover

'''
general results format:

  {
    'recall': {'predicate': [0.0, 1, 0.49, 0.44516129032258067, 0.51, 1.0, 0.0], 'schema': [1.0, 0, 1.0, 0.44516129032258067, 1.0, 1.0, 1.0]},
    'precision': {'predicate': [0, 1, 1.0, 1.0, 1.0, 1.0, 0], 'schema': [0.27044025157232704, 0.0, 1.0, 1.0, 1.0, 0.3333333333333333, 0.01818181818181818]}
  }
'''

class DiagramGenerator:
    
    '''
      "results" received in the constructor:
      
        {'predicate': [0.0, 1, 0.49, 0.44516129032258067, 0.51, 1.0, 0.0], 'schema': [1.0, 0, 1.0, 0.44516129032258067, 1.0, 1.0, 1.0]}
    '''
    def __init__(self, title, ylabel, xlabel, results, ylabel_xaxis):
        self.colors = ('#CFDCE6', '#507EA1', '#406480')
        self.title = title
        self.xlabel = xlabel
        self.results = results
        
        self.ci = ChartImprover( title = title, ylabel = {"label": ylabel, "x": ylabel_xaxis, "y": 1.16} )
        self.generate()

    def generate(self):
        self.fig = plt.figure(figsize=(15,4)) #(figsize=(15,3))
        ax = self.fig.add_subplot(111)
        
        width = 0.25       # the width of the bars
        left_margin = 0.5
        
        i = 0
        for strat_name, values, color in zip( self.results.iterkeys(), self.results.itervalues(), self.colors ):
            N = len(values) # should be always the same
            
            ind = np.arange( left_margin, left_margin + N )  # the x locations for the groups
            left_pos = [ (el + width * i) for el in ind ]
            
            ax.bar( left_pos,
                    values,
                    width,
                    color = color,
                    edgecolor = 'none', # no edges around each bar
                    align = 'center',
                    label = strat_name)
            i += 1
        
        # Set the x tick labels to the group_labels defined above.
        ax.set_xticks( ind + width )
        ax.set_xticklabels( ["t%d"%(i+1) for i in range(N)] )
        ax.set_xlim( 0, N + left_margin )
        
        self.ci.improve_following_guidelines(ax)        
    
    def show(self):
        self.fig.show()
    
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches='tight')

     
def main():
    import json
    f = open('/tmp/clues_precision_recall.json', 'r')
    results = json.loads(f.read())
    f.close()
    
    g = DiagramGenerator('Recall', 'Recall', 'Queries', results["recall"], ylabel_xaxis = 0.02)
    g.save('/tmp/clues_recall.pdf')
    
    g = DiagramGenerator('Precision', 'Precision', 'Queries', results["precision"], ylabel_xaxis = 0.065)
    g.save('/tmp/clues_precision.pdf')
    

if __name__ == '__main__':   
    main()
