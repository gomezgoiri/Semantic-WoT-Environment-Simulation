#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''
import numpy
from matplotlib.ticker import FuncFormatter
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
    def __init__(self, title, ylabel, results): #, formatter=FuncFormatter(bytes)):
        self.title = title
        self.ylabel = ylabel
        self.legends = results.keys()
        #self.formatter = formatter
        self.means = [val['avg'] for val in results.values() ]
        self.std = [val['std'] for val in results.values() ]
        
        self.generate()

    def generate(self):
        x = numpy.arange(len(self.legends)) + 0.3
        width = 0.8       # the width of the bars
        
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        #ax.yaxis.set_major_formatter(self.formatter)
        plt.bar(x, self.means, width, yerr=self.std, color='y', error_kw=dict(elinewidth=6, ecolor='yellow'))
        
        if self.title is not None: plt.title(self.title)
        if self.ylabel is not None: plt.ylabel(self.ylabel)
        
        plt.xticks( x + 0.4,  self.legends )
        plt.draw()
        ax.set_ylim(0)
    
    def show(self):
        plt.show() # does not work in virtualenv
        
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches=0)


def summarizeLenghts(results):
    summarized_results = {}
    summarized_results['schema'] = {}
    summarized_results['predicate'] = {}
    summarized_results['class'] = {}
           
    for g_type in results.keys():
        lengths = results[g_type]
        summarized_results[g_type]['avg'] = numpy.average(lengths)
        summarized_results[g_type]['std'] = numpy.std(lengths)
            
    return summarized_results

def main():
    f = open('/tmp/clues_length.json', 'r')
    results = json.loads(f.read())
    f.close()
    
    sum_res = summarizeLenghts(results)
    
    g = DiagramGenerator(None, "Size of the clues (Bytes)", sum_res)
    g.save('/tmp/clues_length.pdf')

if __name__ == '__main__':
    main()