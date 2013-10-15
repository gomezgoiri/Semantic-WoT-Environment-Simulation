#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

import numpy
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover
from matplotlib.ticker import FuncFormatter


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
        self.legends = results.keys()
        #self.formatter = formatter
        self.means = [val['avg'] for val in results.values() ]
        self.std = [val['std'] for val in results.values() ]
        
        self.ci = ChartImprover( title=title, ylabel={"label": ylabel, "x": 1.001, "y": 1.08} )
        self.generate()

    def generate(self):
        x = numpy.arange(len(self.legends)) + 0.3
        width = 0.8       # the width of the bars
        
        self.fig = plt.figure(figsize=(10,10)) # figsize=(15,4)
        ax = self.fig.add_subplot(111)
        #ax.yaxis.set_major_formatter(self.formatter)
        
        #'#CFDCE6', '#507EA1', '#406480'
        plt.bar( x,
                 self.means,
                 width,
                 yerr=self.std,
                 color='#b2bdc6',
                 edgecolor = 'none',
                 error_kw=dict( elinewidth=10,
                                ecolor='#406480')#'yellow' )
                )
        
        plt.xticks( x + 0.4,  self.legends )
        ax.set_ylim(0)
        
        self.ci.improve_following_guidelines(ax)
    
    def show(self):
        plt.show() # does not work in virtualenv
        
    def save(self, filename):
        self.fig.savefig(filename, bbox_inches=0)


def summarizeLenghts(results):
    summarized_results = {}
    summarized_results['prefix'] = {}
    summarized_results['predicate'] = {}
    summarized_results['class'] = {}
           
    for g_type in results.keys():
        lengths = results[g_type]
        summarized_results[g_type]['avg'] = numpy.average(lengths)
        summarized_results[g_type]['std'] = numpy.std(lengths)
            
    return summarized_results

def main():
    import json
    f = open('/tmp/clues_length.json', 'r')
    results = json.loads(f.read())
    f.close()
    
    sum_res = summarizeLenghts(results)
    
    # TODO the SVG file should be edited manually to put the "Bytes" next to the 500
    ylabel = None # "Size of the clues (Bytes)"
    g = DiagramGenerator(None, ylabel, sum_res)
    g.save('/tmp/clues_length.svg')

if __name__ == '__main__':
    main()