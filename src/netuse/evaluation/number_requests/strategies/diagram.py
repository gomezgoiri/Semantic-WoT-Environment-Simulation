#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt


class DiagramGenerator:
    
    OURS_1C = 'ours_1'
    OURS_10C = 'ours_10'
    OURS_100C = 'ours_100'
    NB = 'nb'
    NUM_NODES = 'num_nodes'
    REQUESTS = 'requests'
    
    '''
      {
        'ours_1': { 'num_nodes': [1,10,50,100,200], 'requests': [[105,100,85],[140,120,130],[376,400,406],[338,320,355],[495,500,505]] },
        'ours_10': { 'num_nodes': [10,50,100,200], 'requests': [[223,220,221],[507,500,510],[430,420,420],[580,600,660]] },
        'ours_100': { 'num_nodes': [100,200], 'requests': [[480,500,520],[640,700,740]] },
        'nb': { 'num_nodes': [1,10,50,100,200], 'requests': [[320,300,340],[420,400,380],[540,600,630],[690,720,710],[880,900,912]] }
      }
    '''
    def __init__(self, title, data):
        self.title = title
        self.xlabel = 'Number of nodes'
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
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.OURS_1C][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.OURS_1C][DiagramGenerator.NUM_NODES],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='ours_1c')
        
        color = colors.next()
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.OURS_10C][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.OURS_10C][DiagramGenerator.NUM_NODES],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='ours_10c')
        
        color = colors.next()
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.OURS_100C][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.OURS_100C][DiagramGenerator.NUM_NODES],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='ours_100c')
        
        color = colors.next()
        means, std_devs = self.get_mean_and_std_dev(data[DiagramGenerator.NB][DiagramGenerator.REQUESTS])
        ax.errorbar( data[DiagramGenerator.NB][DiagramGenerator.NUM_NODES],
                     means, fmt=shapes.next(), color=color,
                     yerr=std_devs, ecolor=color,
                     label='nb')
        
        ax.set_xlim(0)
        ax.set_ylim(0)
        
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
        'ours_1': { 'num_nodes': [1,10,50,100,200], 'requests': [[105,100,85],[140,120,130],[376,400,406],[338,320,355],[495,500,505]] },
        'ours_10': { 'num_nodes': [10,50,100,200], 'requests': [[223,220,221],[507,500,510],[430,420,420],[580,600,660]] },
        'ours_100': { 'num_nodes': [100,200], 'requests': [[480,500,520],[640,700,740]] },
        'nb': { 'num_nodes': [1,10,50,100,200], 'requests': [[320,300,340],[420,400,380],[540,600,630],[690,720,710],[880,900,912]] }
      }
        '''
    json_txt = json_txt.replace(' ','')
    json_txt = json_txt.replace('\n','')
    json_txt = json_txt.replace('\t','')
    
    d = DiagramGenerator("Network usage by strategies", eval(json_txt))
    d.save('/tmp/test_diagram.pdf')

def main():    
    f = open('/tmp/requests_by_strategies.json', 'r')
    json_txt = f.read()
    f.close()
    
    d = DiagramGenerator("Network usage by strategies", eval(json_txt))
    d.save('/tmp/requests_by_strategies.pdf')


if __name__ == '__main__':   
    mainTest()