#!/usr/bin/env python
'''
Created on Jan 08, 2013

@author: tulvur
'''
import numpy as np
from itertools import cycle
from matplotlib.pyplot import FuncFormatter#, LogLocator
import matplotlib.pyplot as plt

def format_time(x, pos):
    """Formatter for Y axis, values are in megabytes"""
    if x<1000:
        return '%1.f ms' % (x)
    elif x<(1000*60):
        return '%1.f s' % (x/(1000))
    elif x<(1000*60*60):
        return '%1.f min' % (x/(1000*60))
    else:
        return '%1.f h' % (x/(1000*60*60))


class DiagramGenerator:
    
    OURS = 'ours'
    NB = 'nb'
    DROP_INTERVAL = 'drop_interval'
    REQUESTS = 'requests'
    
    '''
      {
        'ours': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] },
        'nb': { 'drop_interval': [10000, 60000, 600000, 4000000], 'requests': [[320,300,340],[420,400,380],[690,720,710],[880,900,912]] }
      }
    '''
    def __init__(self, title, data):
        self.title = title
        self.xlabel = 'Drop interval'
        self.ylabel = 'Requests'
        self.linesShapes = ('xk-','+k-.','Dk--')
        self.linesColors = ('r','y','g', 'b')
        self.generate(data)

    def generate(self, data):
        fig = plt.figure()
        
        plt.subplots_adjust(
            left=None,   # the left side of the subplots of the figure
            bottom=None, # the right side of the subplots of the figure
            right=None,  # the bottom of the subplots of the figure
            top=None,    # the top of the subplots of the figure
            wspace=0.3,  # the amount of width reserved for blank space between subplots
            hspace=0.4   # the amount of height reserved for white space between subplots
        )
                
        ax = fig.add_subplot(1,1,1)
        self.generate_subplot(ax, data, self.title)
    
    def get_mean_and_std_dev(self, values):
        means = []
        std_devs = []
        for repetitions in values:
            means.append( np.average(repetitions) )
            std_devs.append( np.std(repetitions) )
        return means, std_devs
    
    def generate_subplot(self, ax, data, title=None):        
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        if title is not None:
            plt.title(title)
        
        shapes = cycle(self.linesShapes)
        colors = cycle(self.linesColors)
        
        color = colors.next()
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.OURS][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.OURS][DiagramGenerator.DROP_INTERVAL],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='ours')
        
        color = colors.next()
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.NB][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.NB][DiagramGenerator.DROP_INTERVAL],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='nb')
        
        ax.set_xlim(0)
        ax.set_ylim(0)
                 
        ax.xaxis.set_major_formatter(FuncFormatter(format_time))
        #ax.xaxis.set_major_locator(LogLocator())
        
        handles, labels = ax.get_legend_handles_labels()
        #ax.legend(handles[::-1], labels[::-1]) # reverse the order
        ax.legend(handles, labels, loc="upper left")
    
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