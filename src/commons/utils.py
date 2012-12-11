'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
import glob
import random
from argparse import ArgumentParser

from rdflib import Graph
from FuXi.Rete.Util import generateTokenSet
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.DLP.DLNormalization import NormalFormReduction



class OwnArgumentParser(ArgumentParser):
    
    def __init__(self, description="Default description"):
        super(OwnArgumentParser, self).__init__(description=description)
        from netuse.results import G
        self.add_argument('-ds','--data-set', default=G.dataset_path, dest='dataset_path',
                    help='Specify the folder containing the dataset to perform the simulation.')

    def parse_args(self):
        from netuse.results import G
        args = super(OwnArgumentParser, self).parse_args()
        G.dataset_path = args.dataset_path
        return args


class SemanticFilesLoader(object):
    
    def __init__(self, path):
        self.path = path
    
    def getStationNames(self, filter_subfolders=None):        
        ret = set()
        dirList=os.listdir( self.path + '/data' )
        for folder in dirList:
            if not folder.startswith(".") and ( (filter_subfolders is None) or (folder in filter_subfolders) ) :
                subdirList = os.listdir( self.path + '/data/' + folder )
                for fname in subdirList:
                    if not fname.startswith("."): # ignore non visible file names
                        ret.add( folder + "/" + fname.partition("_")[0] )
        return ret
    
    def selectStations(self, numberOfNodes="all"):
        possibleNodes = self.getStationNames()
        if numberOfNodes=="all":
            return possibleNodes
        return random.sample(possibleNodes, numberOfNodes)

    def _expand_ontology(self, tBoxGraph):
        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
        NormalFormReduction(tBoxGraph)
        network.setupDescriptionLogicProgramming(tBoxGraph)
        network.feedFactsToAdd(generateTokenSet(tBoxGraph))
        return network.inferredFacts
    
    def loadGraphsJustOnce(self, nodeNames, loadedGraph):
        datasetPath = self.path + "/data"
        ontologiesPath = self.path +"/base_ontologies"
        
        if 'ontology' not in loadedGraph:
            loadedGraph['ontology'] = Graph()
            dirList=os.listdir(ontologiesPath)
            for fname in dirList:
                if not os.path.isdir(ontologiesPath+'/'+fname):
                    loadedGraph['ontology'] += Graph().parse(ontologiesPath+"/"+fname)
            #loadedGraph['ontology_expanded'] = self._expand_ontology(loadedGraph['ontology'])
        
        for node_name in nodeNames:
            if node_name not in loadedGraph:
                loadedGraph[node_name] = []
                for fname in glob.iglob("%s/%s_*.n3"%(datasetPath,node_name)):
                    loadedGraph[node_name].append( Graph().parse(fname, format="n3") )