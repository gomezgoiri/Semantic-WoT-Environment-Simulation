'''
Created on Nov 26, 2011

@author: tulvur
'''
# "SimulationTrace" instead of "Simulation" to debug
import numpy
from itertools import cycle
from matplotlib.pyplot import figure, show, xlabel, ylabel, title
from strateval.database.expected import RequestsResults
from strateval.database.execution import ExecutionSet
from strateval.database.parametrization import Parametrization

class PlotStats(object):
    # http://www.thetechrepo.com/main-articles/469
    def __init__(self, xAxisName=None, yAxisName=None, titleText=None):
        self.linesShapes = cycle(('xk-','+k-.','Dk--'))
        fig = figure()
        self.ax = fig.add_subplot(111)
                
        if xAxisName!=None: xlabel(xAxisName)
        if yAxisName!=None: ylabel(yAxisName)
        if titleText!=None: title(titleText)
    
    def plotLines(self, attributeGetter, lineNames):
        for lineName in lineNames:
            self.plotLine(attributeGetter.getXY(lineName), lineName)
    
    def plotLine(self, xy, lineName, lineShape=None):
        shape = self.linesShapes.next() if lineShape==None else lineShape
        x,y,err = xy
        
        hasError = err!=None and len(err)>0        
        if not hasError:
            self.ax.plot(x, y, shape, label=lineName)
        else:
            self.ax.errorbar(x, y, yerr=err, label=lineName, fmt=shape)
    
    def adjustSettings(self):
        handles, labels = self.ax.get_legend_handles_labels()
        self.ax.legend(handles, labels, loc='best')
        
        self.ax.set_xlim(0)
        self.ax.set_ylim(0)
    
    def show(self):
        self.adjustSettings()
        
        show()


class AttributeGetter:
    
    def __init__(self, attributeGetter, execution_set, x_axis_getter=None):
        self.attributeGetter = attributeGetter
        self.execution_set = execution_set
        # by default nodes changes on the axis
        self.x_axis_getter = x_axis_getter if x_axis_getter!=None else lambda params: params.numberOfNodes 
    
    def getXY(self, strategy):
        data = {}
        for ex in self.execution_set.executions:
            if ex.parameters.strategy == strategy:
                x_val = self.x_axis_getter(ex.parameters)
                data[x_val] = self.attributeGetter(ex)
        
        ordered_keys = data.keys()
        ordered_keys.sort()
        
        x = numpy.array(ordered_keys)
        y = numpy.array([ data[i][0] for i in ordered_keys ])
        
        return x, y, None


class AveragedAttributeGetter:
    
    def __init__(self, attributeGetter, execution_set, x_axis_getter=None, relevancyFilter=None):
        self.attributeGetter = attributeGetter
        self.execution_set = execution_set
        # by default nodes changes on the axis
        self.x_axis_getter = x_axis_getter if x_axis_getter!=None else lambda params: params.numberOfNodes
        self.is_relevant = relevancyFilter if relevancyFilter!=None else lambda params, lineName: params.strategy==lineName
    
    # strategy
    def get_executions_sorted_by_parametrization(self, lineName):
        ret = {}
        i = 0
        
        for ex in self.execution_set.executions:
            
            
            if self.is_relevant(ex.parameters, lineName):
                key = ex.parameters.id
                if key not in ret: ret[key] = []
                if ex.results==None:
                    print ex.parameters, "aaa" 
                else:
                    ret[key].append(self.attributeGetter(ex))
        return ret
    
    def getXY(self, lineName):
        repeated_executions = self.get_executions_sorted_by_parametrization(lineName)
        
        data = {}
        #using "for k,v:" notation a "too many values to unpack exception is thrown
        for params_id in repeated_executions:
            params = Parametrization.objects(id=params_id).first()
            x_val = self.x_axis_getter(params)
            avg_ex = repeated_executions[params_id]
            if x_val not in data: data[x_val] = []
            data[x_val].append( numpy.average(avg_ex) )
            data[x_val].append( numpy.std(avg_ex) )
        
        ordered_keys = data.keys()
        ordered_keys.sort()
        
        x = numpy.array(ordered_keys)
        y = numpy.array([ data[i][0] for i in ordered_keys ])
        err = numpy.array([ data[i][1] for i in ordered_keys ])
        
        return x, y, err


def showTotal():
    for executionSet in ExecutionSet.get_simulated():
        ps = PlotStats(xAxisName="Number of queries",
                       yAxisName="Requests")
        xaxis = lambda params: params.amountOfQueries
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.total, executionSet, x_axis_getter=xaxis)
        ps.plotLines(ag, (Parametrization.centralized, Parametrization.negative_broadcasting))
        
        ps.show()
        break

def showFound():
    for executionSet in ExecutionSet.get_simulated():
        ps = PlotStats(xAxisName="Number of nodes",
                       yAxisName="Number of successful responses",
                       titleText="200 OK")
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.found, executionSet)
        ps.plotLines(ag, (Parametrization.centralized, Parametrization.negative_broadcasting))
        
        ps.show()
        break
    
def showNotFound():
    for executionSet in ExecutionSet.get_simulated():
        ps = PlotStats(xAxisName="Number of nodes",
                       yAxisName="Number of 404s",
                       titleText="404 Not Found")
        ag = AveragedAttributeGetter(lambda ex: ex.results.requests.not_found, executionSet)
        ps.plotLines(ag, (Parametrization.centralized, Parametrization.negative_broadcasting))
        
        ps.show()
        break


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Show experiment results.')
    parser.add_argument('-se','--subexperiment', default='networkOverload', dest='subexperiment',
            help='Specify which experiment you want to use.')
    
    args = parser.parse_args()
    
    if args.subexperiment=='networkOverload':    
        from strateval.main.subexperiments.networkOverload import show
    if args.subexperiment=='responseTime':
        from strateval.main.subexperiments.responseTime import show
    
    showTotal()

if __name__ == '__main__':
    main()