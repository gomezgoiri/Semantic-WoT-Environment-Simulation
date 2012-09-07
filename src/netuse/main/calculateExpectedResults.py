'''
Created on Nov 26, 2011

@author: tulvur
'''
import os
from rdflib import Graph, URIRef
from netuse.database.expected import RequestsResults
from netuse.database.parametrization import Parametrization

def getAllTemplates():
    ret = []
    for par in Parametrization.objects:
        ret += par.queries
    return set(ret)

def calculateExpectedResultsForQueries(queries):
    #queriesAndStNames = getExpectedSimulationResults()
    stNames = getStationNames()
    queriesAndStNames = filterExistingExpectedResults(queries, stNames)
    
    stations = {}
    for name in stNames:
        stations[name] = loadStationContent(name)
    
    for query, station in queriesAndStNames:
        createEntry(query, station, stations)

def getStationNames():
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
    dirList=os.listdir(semanticPath)
    for fname in dirList:
        if not fname.startswith("."): # ignore non visible file names
            ret.append( fname.partition("_")[0] )
        
    # detectOddFiles(ret)
    
    return set(ret)

def filterExistingExpectedResults(queries, stNames):
    ret = []
    
    for q in queries:
        for stName in stNames:
            savedresults = RequestsResults.objects(station_name=stName)
            savedresults = filter(lambda r: r.query==q, savedresults)
            if not savedresults:
                ret.append((q, stName))
    
    return ret # query to check which combinations already exist in the DB

def loadStationContent(stationName):
    ret = Graph()
    dirList=os.listdir(semanticPath)
    for fname in dirList:
        if not os.path.isdir(fname):
            if fname.find(stationName)!=-1:
                ret.parse(semanticPath+"/"+fname, format="n3")
    return ret

def createEntry(query, stationName, stations):
    st = stations[stationName]
    #tr = Graph()
    tr = list(st.triples(query))
    hasResult = bool(tr) # has at least a triple in the response
    
    # calculate if it should contain whether exist
    r = RequestsResults(station_name=stationName, has_result=hasResult, query=query)
    if hasResult:
        print r.station_name, r.query
        
    r.save()



semanticPath = '../../../files/semantic/dataset'

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate expected results.')
    parser.add_argument('-ds','--data-set', default=semanticPath, dest='dataset_path',
                help='Specify the folder containing the dataset to perform the simulation.')
    
    args = parser.parse_args()
    semanticPath = args.dataset_path
    
    queries = getAllTemplates()
    #queries = (
    #           (None, None, None),
    #           (None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_WindDirection")),
    #           (None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_SoilMoisture")),
    #           (None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_SoilTemperature")),
    #           (None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_SnowDepth")), # 13
    #           (None, None, URIRef("http://knoesis.wright.edu/ssw/ont/weather.owl#_PeakWindSpeed")),
    #           )
    
    calculateExpectedResultsForQueries( queries )