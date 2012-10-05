#!/usr/bin/env python
'''
Created on Oct 5, 2012

@author: tulvur
'''
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt


class DiagramGenerator:
    
    PROV_WP = 'prov-WP'
    CONS_WP = 'cons-WP'
    CONS_PROV = 'cons-prov'
    NUM_NODES = 'num_nodes'
    REQUESTS = 'requests'
    
    '''
      {
        'prov-WP': { 'num_nodes': [1,10,50,100,200], 'requests': [100,120,400,320,500] },
        'cons-WP': { 'num_nodes': [10,50,100,200], 'requests': [220,500,420,600] },
        'cons-prov': { 'num_nodes': [100,200], 'requests': [520,700] }
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
        
        ax.plot( data[DiagramGenerator.PROV_WP][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.PROV_WP][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label=DiagramGenerator.PROV_WP)
        
        ax.plot( data[DiagramGenerator.CONS_WP][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.CONS_WP][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label=DiagramGenerator.CONS_WP)
        
        ax.plot( data[DiagramGenerator.CONS_PROV][DiagramGenerator.NUM_NODES],
                 data[DiagramGenerator.CONS_PROV][DiagramGenerator.REQUESTS],
                 shapes.next(), color=colors.next(), label=DiagramGenerator.CONS_PROV)
        
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
        'prov-WP': { 'num_nodes': [1,10,50,100,200], 'requests': [100,120,400,320,500] },
        'cons-WP': { 'num_nodes': [10,50,100,200], 'requests': [220,500,420,600] },
        'cons-prov': { 'num_nodes': [100,200], 'requests': [520,700] }
      }
        '''
    json_txt = json_txt.replace(' ','')
    json_txt = json_txt.replace('\n','')
    json_txt = json_txt.replace('\t','')
    
    d = DiagramGenerator("Roles on the network use", eval(json_txt))
    d.save('/tmp/test_diagram.pdf')

def main():    
    f = open('/tmp/requests_by_roles.json', 'r')
    json_txt = f.read()
    f.close()
    
    d = DiagramGenerator("Roles on the network use", eval(json_txt))
    d.save('/tmp/requests_by_roles.pdf')


if __name__ == '__main__':   
    main()