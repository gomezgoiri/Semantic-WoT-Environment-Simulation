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
        self.color = '#cccccc'
        self.results = results
        self.generate()

    def generateSubplot(self, ax, strategy):
        N = len(strategy[1])
        ind = np.arange( N )  # the x locations for the groups
        width = 0.5       # the width of the bars
        
        ax.bar(ind + width, #*i,
               strategy[1], # width,
               color=self.color,
               align='center')
        
        # add some
        plt.ylabel(self.ylabel)
        plt.title(strategy[0])
 
        # Set the x tick labels to the group_labels defined above.
        ax.set_xticks( ind+width )
        ax.set_xticklabels( ["t%d"%(i+1) for i in range(N)] )
        ax.set_xlim(0,N)

    def generate(self):
        self.fig = plt.figure(figsize=(15,3))
        
        plt.subplots_adjust(
            left=None,   # the left side of the subplots of the figure
            bottom=None, # the right side of the subplots of the figure
            right=None,  # the bottom of the subplots of the figure
            top=None,    # the top of the subplots of the figure
            wspace=0.3,  # the amount of width reserved for blank space between subplots
            hspace=0.4   # the amount of height reserved for white space between subplots
        )
        
        num_strats = len(self.results)
        for strategy, i in zip(self.results.iteritems(), range(num_strats)):
            ax = self.fig.add_subplot(1,num_strats,i)
            self.generateSubplot(ax, strategy)
    
    def show(self):
        self.fig.show()
    
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches='tight')

     
def main():
    f = open('/tmp/clues_precision_recall.json', 'r')
    results = json.loads(f.read())
    f.close()
    
    g = DiagramGenerator('Recall', 'Recall for each query', results["recall"])
    g.save('/tmp/clues_recall.pdf')
    
    g = DiagramGenerator('Precision', 'Precision for each query', results["precision"])
    g.save('/tmp/clues_precision.pdf')
    

if __name__ == '__main__':   
    main()
