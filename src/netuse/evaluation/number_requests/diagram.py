#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt


class DiagramGenerator:
    
    OURS = 'ours'
    NB = 'nb'
    NUM_NODES = 'num_nodes'
    REQUESTS = 'requests'
    
    '''
      {
         'total': {
             'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
             'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
         },
         'white_pages': {
             'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
             'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
         },
        'consumers': {
             'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
             'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
         },
        'providers': {
             'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
             'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
         }
      }
    '''
    def __init__(self, title, data):
        self.title = title
        self.xlabel = 'Number of nodes'
        self.ylabel = 'Requests'
        self.linesShapes = ('xk-','+k-.','Dk--')
        self.linesColors = ('r','y','g')
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
                
        ax = fig.add_subplot(2,2,1)
        self.generate_subplot(ax, data['total'], "Total")
        
        ax = fig.add_subplot(2,2,2)
        self.generate_subplot(ax, data['white_pages'], "White Pages")
        
        ax = fig.add_subplot(2,2,3)
        self.generate_subplot(ax, data['consumers'], "Consumers")
        
        ax = fig.add_subplot(2,2,4)
        self.generate_subplot(ax, data['providers'], "Providers")
    
    def generate_subplot(self, ax, data, title):        
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(title)
        
        shapes = cycle(self.linesShapes)
        colors = cycle(self.linesColors)
        
        ax.plot( data[DiagramGenerator.OURS][DiagramGenerator.NUM_NODES],
                      data[DiagramGenerator.OURS][DiagramGenerator.REQUESTS],
                      shapes.next(), color=colors.next(), label='ours')
        
        ax.plot( data[DiagramGenerator.NB][DiagramGenerator.NUM_NODES],
                      data[DiagramGenerator.NB][DiagramGenerator.REQUESTS],
                      shapes.next(), color=colors.next(), label='ours')
        
        ax.set_xlim(0)
        ax.set_ylim(0)
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches=0)
        
if __name__ == '__main__':
    
    json = '''
              {
                 'total': {
                     'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
                     'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
                 },
                 'white_pages': {
                     'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
                     'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
                 },
                'consumers': {
                     'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
                     'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
                 },
                'providers': {
                     'ours': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] },
                     'nb': { 'num_nodes': [1,20,50,100,200], 'requests': [100,120,400,320,500] }
                 }
              }
            '''
    json = json.replace(' ','')
    json = json.replace('\n','')
    json = json.replace('\t','')
    
    d = DiagramGenerator("Net usage", eval(json))
    #d.show()
    #raw_input("Press ENTER to exit")
    d.save('/tmp/example.pdf')