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

import numpy as np
from itertools import cycle
from matplotlib.pyplot import FuncFormatter, MultipleLocator
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover


def format_time_in_minutes(x, pos):
    """Formatter for Y axis, values are in miliseconds"""
    return '%1.f' % (x/(1000*60))

def format_time(x, pos):
    """Formatter for Y axis, values are in time units"""
    if x<1000:
        return '%1.f ms' % (x)
    elif x<(1000*60):
        return '%1.f s' % (x/(1000))
    elif x<(1000*60*60):
        return '%1.f min' % (x/(1000*60))
    else:
        return "Never" #'%1.f h' % (x/(1000*60*60))


class DiagramGenerator:
    
    NB = 'nb'
    OURS = 'ours' # total
    PROV_WP = 'prov-WP'
    CONS_WP = 'cons-WP'
    CONS_PROV = 'cons-prov'
    DROP_INTERVAL = 'drop_interval'
    REQUESTS = 'requests'
    
    '''
      {
        'ours': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] },
        'nb': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] }
        (...possibly more labels...)
      }
    '''
    def __init__(self, title, data):
        # http://colorschemedesigner.com/previous/colorscheme2/index-es.html?tetrad;100;0;225;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0
        self.linesColors = cycle(("#BF60BF", "#ACBF60", "#BF9060", "#6096BF"))
        self.ci = ChartImprover( title = None, # title,
                                 xlabel = 'Drop-interval (mins)',
                                 ylabel = {"label": 'Requests', "x": -0.02, "y": 1.1},
                                 legend_from_to = (0.2, 0.8) )
        #self.linesShapes = cycle(('xk-','+k-.','Dk--'))
        self.generate(data)

    def generate(self, data):
        fig = plt.figure(figsize=(16,6))
        
        show_on_diagram = ( DiagramGenerator.NB,
                            DiagramGenerator.OURS )
        ax1 = fig.add_subplot(1,2,1)
        self.generate_subplot(ax1, data, show_on_diagram)
        
        
        show_on_diagram = ( DiagramGenerator.PROV_WP,
                            DiagramGenerator.CONS_WP)
        ax2 = fig.add_subplot(1,2,2)
        self.generate_subplot(ax2, data, show_on_diagram)    
    
    
    def get_mean_and_std_dev(self, values):
        means = []
        std_devs = []
        for repetitions in values:
            means.append( np.average(repetitions) )
            std_devs.append( np.std(repetitions) )
        return means, std_devs
    
    def generate_subplot(self, ax, data, show_on_diagram, title=None):        
        for label in show_on_diagram:
            color = self.linesColors.next()
            means, std_devs = self.get_mean_and_std_dev(data[label][DiagramGenerator.REQUESTS])
            ax.errorbar( data[label][DiagramGenerator.DROP_INTERVAL],
                         means,
                         #fmt = self.linesShapes.next(),
                         color = color,
                         #yerr = std_devs, ecolor = color, # in this print N=1, so avoiding errorbars it looks better
                         label = label)
        
        ax.set_xlim(0)
        ax.set_ylim(0)
                 
        ax.xaxis.set_major_formatter(FuncFormatter(format_time_in_minutes))
        ax.xaxis.set_major_locator(MultipleLocator( 1000*60*10 )) # each 10 minutes a tick
        
        self.ci.improve_following_guidelines(ax)
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches='tight')


def mainTest():
    json_txt = '''
      {
        'ours': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] },
        'nb': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] }
      }
        '''
    json_txt = json_txt.replace(' ','')
    json_txt = json_txt.replace('\n','')
    json_txt = json_txt.replace('\t','')
    
    d = DiagramGenerator("Solutions behavior on dynamic environments", eval(json_txt))
    d.save('/tmp/test_diagram.pdf')

def main():    
    f = open('/tmp/dynamism.json', 'r')
    json_txt = f.read()
    f.close()
    
    d = DiagramGenerator("Solutions behavior on dynamic environments", eval(json_txt))
    d.save('/tmp/dynamism.svg')


if __name__ == '__main__':   
    main()