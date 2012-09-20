'''
Created on Aug 17, 2012

@author: tulvur
'''
#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

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
    def __init__(self, title, ylabel, results):
        self.title = title
        self.ylabel = ylabel
        self.legends = results.keys()
        self.bars = results.values()
        self.N = len(self.bars[0])
        
        self.generate()

    def generate(self):
        
        ind = np.arange(self.N)  # the x locations for the groups
        width = 0.25       # the width of the bars
        
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        
        rects = []
        i = 0
        for bar, color in zip(self.bars, ('r', 'y', 'g')):
            rects.append(ax.bar(ind + width*i, bar, width, color=color))
            i+=1
        
        # add some
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.xticks(ind+width, ["Q%d"%(i) for i in range(self.N)] )
        
        plt.legend( rects, self.legends )
    
    def show(self):
        self.fig.show()
    
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches=0)