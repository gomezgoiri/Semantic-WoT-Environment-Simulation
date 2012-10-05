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
        'ours_1': { 'num_nodes': [1,10,50,100,200], 'requests': [100,120,400,320,500] },
        'ours_10': { 'num_nodes': [10,50,100,200], 'requests': [220,500,420,600] },
        'ours_100': { 'num_nodes': [100,200], 'requests': [520,700] },
        'nb': { 'num_nodes': [1,10,50,100,200], 'requests': [300,420,600,720,900] }
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
    
    def generate_subplot(self, ax, data, title=None):        
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        if title is not None:
            plt.title(title)
        
        shapes = cycle(self.linesShapes)
        colors = cycle(self.linesColors)
        
        ax.plot( data[DiagramGenerator.OURS_1C][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.OURS_1C][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label='ours_1c')
        
        ax.plot( data[DiagramGenerator.OURS_10C][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.OURS_10C][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label='ours_10c')
        
        ax.plot( data[DiagramGenerator.OURS_100C][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.OURS_100C][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label='ours_100c')
        
        ax.plot( data[DiagramGenerator.NB][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.NB][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label='nb')
        
        ax.set_xlim(0)
        ax.set_ylim(0)
        
        handles, labels = ax.get_legend_handles_labels()
        #ax.legend(handles[::-1], labels[::-1]) # reverse the order
        ax.legend(handles, labels, loc="upper left")
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches=0)


def main():
#    json = '''
#          {
#    'ours_1': { 'num_nodes': [1,10,50,100,200], 'requests': [100,120,400,320,500] },
#    'ours_10': { 'num_nodes': [10,50,100,200], 'requests': [220,500,420,600] },
#    'ours_100': { 'num_nodes': [100,200], 'requests': [520,700] },
#    'nb': { 'num_nodes': [1,10,50,100,200], 'requests': [300,420,600,720,900] }
#          }
#        '''
#    json = json.replace(' ','')
#    json = json.replace('\n','')
#    json = json.replace('\t','')
    
    f = open('/tmp/strategies_eval.json', 'r')
    json_txt = f.read()
    f.close()
    
    d = DiagramGenerator("Network usage", eval(json_txt))
    d.save('/tmp/diagram.pdf')
        
    #d.show()
    #raw_input("Press ENTER to exit")


if __name__ == '__main__':   
    main()