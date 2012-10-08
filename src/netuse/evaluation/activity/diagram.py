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
    TOTAL = 'total'
    
    '''
      {
        'ours': {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             ...,
             'devn': 510
         },
        'nb': {
            'total': 320
        }
      }
    '''
    def __init__(self, title, data):
        self.title = title
        self.xlabel = 'Number of nodes'
        self.ylabel = 'active time / node'
        self.colors =  cycle(('r','y','g'))
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
                
        ax1 = fig.add_subplot(1,2,1)
        self.generate_subplot_strategy_comparison(ax1, data)
        
        ax2 = fig.add_subplot(1,2,2)
        self.generate_subplot_ours_device_comparison(ax2, data)
        
        if ax1.get_ylim()>ax2.get_ylim():
            ax2.set_ylim(ax1.get_ylim())
        else:
            ax1.set_ylim(ax2.get_ylim())
    
    def generate_subplot_strategy_comparison(self, ax, data):        
        plt.xlabel("Strategy")
        plt.ylabel(self.ylabel)
        
        
        ind = (1,2)  # the x locations for the groups
        width = 0.5       # the width of the bars
        
        ax.bar( ind,
                (data[DiagramGenerator.NB][DiagramGenerator.TOTAL],
                 data[DiagramGenerator.OURS][DiagramGenerator.TOTAL]),
               width, color=self.colors.next())
        plt.xticks([i+width/2 for i in ind ], ('nb', 'ours') )
        
        ax.set_xlim(0.5,3)
        ax.set_ylim(0)
    
    def generate_subplot_ours_device_comparison(self, ax, data):        
        plt.xlabel("Types of devices")
        plt.ylabel(self.ylabel)
        
        elements = dict(data[DiagramGenerator.OURS])
        del elements[DiagramGenerator.TOTAL]
        
        ind = range(1, len(elements)+1) # the x locations for the groups
        width = 0.5       # the width of the bars
        
        print elements.values()
        ax.bar( ind,
                elements.values(),
                width, color=self.colors.next())
        plt.xticks([i+width/2 for i in ind], elements.keys() )
        
        ax.set_xlim(0.5, len(elements)+1)
        ax.set_ylim(0)
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches=0)
        

def mainTest():
    json_txt = '''{
        'ours': {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             'dev3': 510
         },
        'nb': {
            'total': 320
        }
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
    mainTest()