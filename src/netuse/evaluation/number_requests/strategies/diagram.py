#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover


class DiagramGenerator:
    
    NB_CACHING_1C = 'caching_1'
    NB_CACHING_100C = 'caching_100'
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
        
        # http://colorschemedesigner.com/previous/colorscheme2/index-es.html?tetrad;100;0;225;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0
        self.linesColors = ("#E6AC73", "#CFE673", "#507EA1", "#E67373", "#8A458A")
        # self.linesShapes = ('xk-','+k-.','Dk--') # avoiding spaghetti lines
        self.ci = ChartImprover( title = None, # title,
                                 xlabel = 'Number of nodes',
                                 ylabel = {"label": 'Requests', "x": -0.02, "y": 1.1},
                                 legend_from_to = (0.04, 1.0) )
        # from worst to best
        desired_order = ( DiagramGenerator.NB,
                          DiagramGenerator.NB_CACHING_100C,
                          DiagramGenerator.OURS_100C,
                          DiagramGenerator.OURS_10C,
                          DiagramGenerator.OURS_1C,
                          DiagramGenerator.NB_CACHING_1C )
        self.generate(data, desired_order)
    
    def get_mean_and_std_dev(self, values):
        means = []
        std_devs = []
        for repetitions in values:
            means.append( np.average(repetitions) )
            std_devs.append( np.std(repetitions) )
        return means, std_devs
    
    def generate(self, data, desired_order):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1,1,1)
        
        #shapes = cycle(self.linesShapes)
        colors = cycle(self.linesColors)
        
        #for strategy_name, strat_data in data.iteritems():
        # I want they to appear in an order: for the legends and for the colors
        for strategy_name in desired_order:
            if strategy_name in data:
                strat_data = data[strategy_name]
                color = colors.next()
                means, std_devs = self.get_mean_and_std_dev(strat_data[DiagramGenerator.REQUESTS])
                ax.errorbar( strat_data[DiagramGenerator.NUM_NODES],
                             means, #fmt = shapes.next(),
                             color = color,
                             yerr = std_devs, ecolor = color,
                             label = strategy_name )
        
        ax.set_xlim(0)
        ax.set_ylim(0)
        
        self.ci.improve_following_guidelines(ax)
        handles, labels = ax.get_legend_handles_labels()
        #ax.legend(handles[::-1], labels[::-1]) # reverse the order
        ax.legend(handles, labels, loc="upper right")
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches='tight')


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
    d.save('/tmp/requests_by_strategies.svg')


if __name__ == '__main__':   
    main()