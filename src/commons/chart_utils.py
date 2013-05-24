'''
Created on May 23, 2013

@author: tulvur
'''

import matplotlib.pyplot as plt
import matplotlib

class ChartImprover(object):
    
    def __init__(self, title=None, xlabel=None, ylabel={'label': None, 'x':0, 'y': 0 }):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self._configure_matplotlib()
    
    # should be called before making the chart
    def _configure_matplotlib(self):
        # change font
        matplotlib.rcParams.update({'font.size': 24})
        
        # change paddings for ticks
        matplotlib.rcParams['xtick.major.pad']='12'
        matplotlib.rcParams['ytick.major.pad']='12'
        
        # Line thickness
        matplotlib.rcParams['lines.linewidth'] = 5

    def improve_following_guidelines(self, ax): # from the Wall Street Journal "Guide to Information Graphics"
        #ax.legend(handles, labels, loc="upper right")
        leg = ax.legend(bbox_to_anchor=(0.12, 1.1, .78, .102), loc=3, ncol=3, mode="expand", borderaxespad=0)
        if leg is not None: # we got labels to create a legend
            leg.get_frame().set_alpha(0)
        
        # add some labels to the chart
        if self.title is not None: plt.title( self.title )
        if self.xlabel is not None: plt.xlabel( self.xlabel, labelpad=20 )
        if self.ylabel is not None and self.ylabel['label'] is not None:
            plt.ylabel( self.ylabel['label'], rotation='horizontal' )# verticalalignment="top")
            ax.yaxis.set_label_coords( self.ylabel['x'], self.ylabel['y'] )
        #plt.xlabel(self.xlabel, labelpad=20)
        
        # Just horizontal grid line and in the foreground
        #ax.grid(True)
        ax.yaxis.grid( True )
        ax.xaxis.grid( False )
        ax.set_axisbelow( True )
        
        # from: http://stackoverflow.com/questions/9126838/how-to-simultaneously-remove-top-and-right-axes-and-plot-ticks-facing-outwards
        
        #do not display top and right axes
        #comment to deal with ticks
        ax.spines["left"].set_visible( False )
        ax.spines["right"].set_visible( False )
        ax.spines["top"].set_visible( False )
        
        # omit ticks
        # the OP way (better):
        ax.tick_params( axis='both', direction='out' )
        ax.get_xaxis().tick_bottom() # remove unneeded ticks 
        ax.get_yaxis().tick_left()