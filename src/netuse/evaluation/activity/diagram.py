#!/usr/bin/env python
'''
Created on Aug 18, 2012

@author: tulvur
'''

import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt
from commons.chart_utils import ChartImprover
from matplotlib.ticker import FuncFormatter


def seconds(x, pos):
    'The two args are the value and tick position'
    return '%d' % (x/1000.0)


class DiagramGenerator:
    
    OURS = 'ours'
    NB = 'nb'
    TOTAL = 'total'
    
    '''
      {
        'ours': [
            {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             ...,
             'devn': 510
            },
            ...
            {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             ...,
             'devn': 510
            }
        ],
        'nb': [
            {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             ...,
             'devn': 510
            },
            ...
            {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             ...,
             'devn': 510
            }
        ]
      }
    '''
    def __init__(self, data):
        # http://colorschemedesigner.com/previous/colorscheme2/index-es.html?tetrad;100;0;225;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0.3;-0.8;0.3;0.5;0.1;0.9;0.5;0.75;0
        self.colors =  cycle(('#CF6795','#E6DA73', "#507EA1"))
        self.ci = ChartImprover( # There should be two distinct x labels: ('Strategy', 'device type'),
                                 legend_from_to = (0.25, 0.55) )
        self.generate(data)

    def generate(self, data):
        formatter = FuncFormatter(seconds)
        
        fig = plt.figure(figsize=(18,6))
                
        ax1 = fig.add_subplot(1,2,1)
        ax1.yaxis.set_major_formatter(formatter)
        self.generate_subplot_strategy_comparison(ax1, data)
        
        ax2 = fig.add_subplot(1,2,2)
        ax2.yaxis.set_major_formatter(formatter)
        self.generate_subplot_device_comparison(ax2, data)
        
        if ax1.get_ylim()>ax2.get_ylim():
            ax2.set_ylim(ax1.get_ylim())
        else:
            ax1.set_ylim(ax2.get_ylim())
    
    def generate_subplot_strategy_comparison(self, ax, data):        
        #total_nb = [rep[DiagramGenerator.TOTAL] for rep in data[DiagramGenerator.NB] ]
        #total_ours = [rep[DiagramGenerator.TOTAL] for rep in data[DiagramGenerator.OURS] ]
        
        values = ( data[DiagramGenerator.NB][DiagramGenerator.TOTAL], data[DiagramGenerator.OURS][DiagramGenerator.TOTAL] )
        #values = (np.average(total_nb), np.average(total_ours))
        #yerr = data[DiagramGenerator.NB][DiagramGenerator.TOTAL] #(np.std(total_nb), np.std(total_ours))
        
        ind = (1,2)  # the x locations for the groups
        width = 0.5       # the width of the bars
        
        ax.bar( ind,
                values,
                width,
                #yerr=yerr,
                color=self.colors.next(),
                #ecolor='black'
                edgecolor = 'none' )
        plt.xticks([i+width/2 for i in ind ], ('nb', 'ours') )
        
        ax.set_xlim(0.5,3)
        ax.set_ylim(0)
        
        self.ci.improve_following_guidelines(ax)
        
    def _generate_dictionary_by_device(self, strategy_list):       
        devices = {}
        for rep in strategy_list:
            for device_name, meas in rep.iteritems():
                if device_name is not DiagramGenerator.TOTAL:
                    if device_name not in devices:
                        devices[device_name] = []
                    devices[device_name].append(meas)
        return devices
    
    def _check_order(self, devices_nb, devices_ours):
        for nb_dev_names, ours_dev_names in zip(devices_nb.iterkeys(), devices_ours.iterkeys()):
            if nb_dev_names!=ours_dev_names:
                raise Exception("Error. Both list should have keys in the same order.")
            
    
    def generate_subplot_device_comparison(self, ax, data):        
        #devices_nb = self._generate_dictionary_by_device(data[DiagramGenerator.NB])
        #devices_ours = self._generate_dictionary_by_device(data[DiagramGenerator.OURS])
        #self._check_order(devices_nb, devices_ours)
        
        self._check_order(data[DiagramGenerator.NB], data[DiagramGenerator.OURS])
        devices_names = data[DiagramGenerator.NB].keys()
        devices_names.remove( DiagramGenerator.TOTAL )
        ind = range(1, len(devices_names)+1) # the x locations for the groups
        width = 0.3       # the width of the bars
        
        
        values = [ v for k, v in data[DiagramGenerator.NB].iteritems() if k != DiagramGenerator.TOTAL ]
        #values = [np.average(measures) for measures in devices_nb.itervalues()]
        #yerr = [np.std(measures) for measures in devices_nb.itervalues()]
        
        ax.bar( ind, values, width,
                #yerr=yerr,
                color=self.colors.next(),
                #ecolor='black',
                edgecolor = 'none',
                label=DiagramGenerator.NB
        )
        
        
        values = [ v for k, v in data[DiagramGenerator.OURS].iteritems() if k != DiagramGenerator.TOTAL ]
        #values = [np.average(measures) for measures in devices_ours.itervalues()]
        #yerr = [np.std(measures) for measures in devices_ours.itervalues()]
        
        ax.bar( [i+width for i in ind], values, width,
                #yerr=yerr,
                color=self.colors.next(),
                #ecolor='black',
                edgecolor = 'none',
                label=DiagramGenerator.OURS
        )
        
        
        plt.xticks( [i+width for i in ind], devices_names)
        
        ax.set_xlim(0.5, len(devices_names)+1)
        ax.set_ylim(0)
        
        self.ci.improve_following_guidelines(ax)
    
    def show(self):
        plt.show()
        
    def save(self, filename):
        plt.savefig(filename, bbox_inches='tight')
        

def mainTest():
    json_txt = '''{
        'ours': [
            {
             'total': 120,
             'dev1': 320,
             'dev2': 420,
             'dev3': 510
            },
            {
             'total': 140,
             'dev1': 120,
             'dev2': 420,
             'dev3': 510
            },
        ],
        'nb': [
            {
             'total': 360,
             'dev1': 120,
             'dev2': 120,
             'dev3': 120
            },
            {
             'total': 380,
             'dev1': 140,
             'dev2': 120,
             'dev3': 120
            },
            {
             'total': 320,
             'dev1': 120,
             'dev2': 120,
             'dev3': 80
            },
        ]
    }
    '''
    json_txt = json_txt.replace(' ','')
    json_txt = json_txt.replace('\n','')
    json_txt = json_txt.replace('\t','')
    
    d = DiagramGenerator(eval(json_txt))
    d.save('/tmp/test_diagram.pdf')

def main():    
    f = open('/tmp/activity_measures.json', 'r')
    json_txt = f.read()
    f.close()
    
    d = DiagramGenerator(eval(json_txt))
    d.save('/tmp/activity_measures.svg')


if __name__ == '__main__':   
    main()