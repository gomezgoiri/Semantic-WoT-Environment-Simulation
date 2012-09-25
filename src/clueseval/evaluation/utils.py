'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
import random
from rdflib import Graph
import glob


def getStationNames(semanticPath):
    def detectOddFiles(list):
        k = {}
        for e in list:
            if not k.has_key(e):
                k[e] = 0
            k[e] += 1
        
        for e in k:
            if k[e]==1:
                print e
    
    ret = []
    dirList=os.listdir(semanticPath+'/data')
    for fname in dirList:
        if not fname.startswith("."): # ignore non visible file names
            ret.append( fname.partition("_")[0] )
        
    # detectOddFiles(ret)
    
    return set(ret)

def selectStations(semanticPath, numberOfNodes="all"):
    possibleNodes = getStationNames(semanticPath)
    if numberOfNodes=="all":
        return possibleNodes
    return random.sample(possibleNodes, numberOfNodes)

def loadGraphsJustOnce(nodeNames, semanticPath, loadedGraph):
    datasetPath = semanticPath+"/data"
    ontologiesPath = semanticPath+"/base_ontologies"
    
    if 'ontology' not in loadedGraph:
        loadedGraph['ontology'] = Graph()
        dirList=os.listdir(ontologiesPath)
        for fname in dirList:
            if not os.path.isdir(ontologiesPath+'/'+fname):
                loadedGraph['ontology'] += Graph().parse(ontologiesPath+"/"+fname)
        #loadedGraph['ontology_expanded'] = expand_ontology(loadedGraph['ontology'])
    
    for node_name in nodeNames:
        if node_name not in loadedGraph:
            loadedGraph[node_name] = []
            for fname in glob.iglob("%s/%s_*.n3"%(datasetPath,node_name)):
                loadedGraph[node_name].append( Graph().parse(fname, format="n3") )