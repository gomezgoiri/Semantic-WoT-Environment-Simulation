#!/usr/bin/env python
'''
Created on Oct 5, 2012

@author: tulvur
'''
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover


class DiagramGenerator:
    
    PROV_WP = 'prov-WP'
    CONS_WP = 'cons-WP'
    CONS_PROV = 'cons-prov'
    NUM_NODES = 'num_nodes'
    REQUESTS = 'requests'
    
    '''
      {
        'prov-WP': { 'num_nodes': [1,10,50,100,200], 'requests': [[105,100,85],[140,120,130],[376,400,406],[338,320,355],[495,500,505]] },
        'cons-WP': { 'num_nodes': [10,50,100,200], 'requests': [[223,220,221],[507,500,510],[430,420,420],[580,600,660]] },
        'cons-prov': { 'num_nodes': [100,200], 'requests': [[480,500,520],[640,700,740]] }
      }
    '''
    def __init__(self, title, data):
        
        self.linesColors = ("#CF6795", "#BFB130", "#507EA1") # ('r','y','g', 'b')
        # self.linesShapes = ('xk-','+k-.','Dk--') # avoiding spaghetti lines
        self.ci = ChartImprover( title = None, # title,
                                 xlabel = 'Number of nodes',
                                 ylabel = {"label": 'Requests', "x": -0.02, "y": 1.08} )
        
        self.generate(data)

    def generate(self, data):
        fig = plt.figure(figsize=(15,10))                
        ax = fig.add_subplot(1,1,1)
        self.generate_subplot(ax, data)
        
    def get_mean_and_std_dev(self, values):
        means = []
        std_devs = []
        for repetitions in values:
            means.append( np.average(repetitions) )
            std_devs.append( np.std(repetitions) )
        return means, std_devs
    
    def generate_subplot(self, ax, data, title=None):
        #shapes = cycle(self.linesShapes)
        colors = cycle(self.linesColors)
        
        for role_name, strat_data in data.iteritems():
            color = colors.next()
            means, std_devs = self.get_mean_and_std_dev(strat_data[DiagramGenerator.REQUESTS])
            ax.errorbar( strat_data[DiagramGenerator.NUM_NODES],
                         means, #fmt = shapes.next(),
                         color = color,
                         yerr = std_devs, ecolor = color,
                         label = role_name )
        
        ax.set_xlim(0)
        ax.set_ylim(0)
        
        self.ci.improve_following_guidelines(ax)
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches='tight')

def mainTest():
    json_txt = '''
      {
        'prov-WP': { 'num_nodes': [1,10,50,100,200], 'requests': [[105,100,85],[140,120,130],[376,400,406],[338,320,355],[495,500,505]] },
        'cons-WP': { 'num_nodes': [10,50,100,200], 'requests': [[223,220,221],[507,500,510],[430,420,420],[580,600,660]] },
        'cons-prov': { 'num_nodes': [100,200], 'requests': [[480,500,520],[640,700,740]] }
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