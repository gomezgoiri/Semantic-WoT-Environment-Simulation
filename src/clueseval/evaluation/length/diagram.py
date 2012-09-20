#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''
from matplotlib.ticker import FuncFormatter
import numpy as np
import matplotlib.pyplot as plt

mean = (1020, 4035, 530)
std =   (200, 300, 400)

def kilobytes(x, pos):
    'The two args are the value and tick position'
    return '%1.1fKB' % (x/1024.0)

def bytes(x, pos):
    return '%1.1fB' % (x)


class DiagramGenerator:
    
    '''
      {'predicate': {'std': 231.9287686342191, 'avg': 500.67924528301887}, 'class': {'std': 255.84400354001542, 'avg': 287.69811320754718}, 'schema': {'std': 119.75312693100898, 'avg': 401.21698113207549}}
    '''
    def __init__(self, title, ylabel, results, formatter=FuncFormatter(bytes)):
        self.title = title
        self.ylabel = ylabel
        self.legends = results.keys()
        self.formatter = formatter
        self.means = [val['avg'] for val in results.values() ]
        self.std = [val['std'] for val in results.values() ]
        
        self.generate()

    def generate(self):
        x = np.arange(len(self.legends)) + 0.3
        width = 0.8       # the width of the bars
        
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        ax.yaxis.set_major_formatter(self.formatter)
        plt.bar(x, self.means, width, yerr=self.std, color='y', error_kw=dict(elinewidth=6, ecolor='yellow'))
        
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.xticks( x + 0.4,  self.legends )
        plt.draw()
    
    def show(self):
        plt.show() # does not work in virtualenv
        
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches=0)
        
if __name__ == '__main__':
    d = DiagramGenerator("blah", "blahblah",
                         eval("{'predicate': {'std': 200, 'avg': 1020}, 'class': {'std': 300, 'avg': 4035}, 'schema': {'std': 400, 'avg': 530}}"),
                         formatter=FuncFormatter(kilobytes))
    d.show()
    raw_input("Press ENTER to exit")