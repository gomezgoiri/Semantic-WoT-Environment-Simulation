# -*- coding: utf-8 -*-
'''
 Copyright (C) 2012 onwards University of Deusto
  
 All rights reserved.
 
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.
 
 This software consists of contributions made by many individuals, 
 listed below:
 
 @author: Aitor Gómez Goiri <aitor.gomez@deusto.es>
'''

from rdflib import RDF
from commons.utils import SemanticFilesLoader
from numpy import mean, std

class DescriptiveStatistics(object):
    
    def __init__(self, sp):
        self.load_graphs(sp)
        
        self.types = {}
        self.types['total'] = set()
        self.predicates = {}
        self.predicates['total'] = set()
        
        for key in self.graphs.iterkeys():
            if key not in ('ontology','ontology_expanded'):
                self.types[key] = set()
                self.predicates[key] = set()
        
        self.load_data_for_stats()
    
    def load_graphs(self, semanticPath):
        sfl = SemanticFilesLoader(semanticPath)
        names = sfl.selectStations()
        self.graphs = {}
        sfl.loadGraphsJustOnce(names, self.graphs)
    
    def load_data_for_stats(self):
        for k, v in self.graphs.iteritems():
            if k not in ('ontology','ontology_expanded'):
                for graph in v:
                    self.extractTypes(graph, k)
                    self.extractPredicates(graph, k)
                # Now that I have the sets, I can just store the total
                self.types[k] = len(self.types[k])
                self.predicates[k] = len(self.predicates[k])
        self.types['total'] = len(self.types['total'])
        self.predicates['total'] = len(self.predicates['total'])
    
    def extractTypes(self, graph, key):
        for t in graph.triples((None, RDF.type, None)):
            self.types[key].add(t[2])
            self.types['total'].add(t[2])
    
    def extractPredicates(self, graph, key):
        for t in graph.triples((None, None, None)):
            self.predicates[key].add(t[1])
            self.predicates['total'].add(t[1])
    
    def print_stats(self):
        print "Classes"
        tt = self.types['total']
        del self.types['total']
        
        tm = mean(self.types.values())
        ts = std(self.types.values())
        print "total: %.2f, mean: %.2f, std dev: %.2f"%(tt, tm, ts)
        
        print "Predicates"
        tp = self.predicates['total']
        del self.predicates['total']
        
        mp = mean(self.predicates.values())
        sp = std(self.predicates.values())
        print "total: %.2f, mean: %.2f, std dev: %.2f"%(tp, mp, sp)

        
if __name__ == '__main__':
    import argparse
    
    semanticPath = '/home/tulvur/dev/dataset'
    
    parser = argparse.ArgumentParser(description='Evaluate gossiping strategies.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    args = parser.parse_args()
    
    ds = DescriptiveStatistics(semanticPath)
    ds.print_stats()