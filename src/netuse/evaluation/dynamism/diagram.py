#!/usr/bin/env python
'''
Created on Jan 08, 2013

@author: tulvur
'''
import numpy as np
from itertools import cycle
from matplotlib.pyplot import FuncFormatter#, LogLocator
import matplotlib.pyplot as plt


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
        self.title = title
        self.xlabel = 'Drop interval (mins)'
        self.ylabel = 'Requests'
        self.linesShapes = cycle(('xk-','+k-.','Dk--'))
        self.linesColors = cycle(('r','g', 'b','y'))
        self.generate(data)

    def generate(self, data):
        fig = plt.figure(figsize=(10,5))
        
        plt.subplots_adjust(
            left=None,   # the left side of the subplots of the figure
            bottom=None, # the right side of the subplots of the figure
            right=None,  # the bottom of the subplots of the figure
            top=None,    # the top of the subplots of the figure
            wspace=0.3,  # the amount of width reserved for blank space between subplots
            hspace=0.4   # the amount of height reserved for white space between subplots
        )
        
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
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        if title is not None:
            plt.title(title)
        
        for label in show_on_diagram:
            color = self.linesColors.next()
            means, std_devs = self.get_mean_and_std_dev(data[label][DiagramGenerator.REQUESTS])
            ax.errorbar( data[label][DiagramGenerator.DROP_INTERVAL],
                         means, fmt = self.linesShapes.next(), color = color,
                         yerr = std_devs, ecolor = color,
                         label = label)
        
        ax.set_xlim(0)
        ax.set_ylim(0)
                 
        ax.xaxis.set_major_formatter(FuncFormatter(format_time_in_minutes))
        #ax.xaxis.set_major_locator(LogLocator())
        
        handles, labels = ax.get_legend_handles_labels()
        #ax.legend(handles[::-1], labels[::-1]) # reverse the order
        ax.legend(handles, labels, loc="upper right")
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches=0)


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
    d.save('/tmp/dynamism.pdf')


if __name__ == '__main__':   
    main()