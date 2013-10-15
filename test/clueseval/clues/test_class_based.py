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

import unittest
from rdflib import RDF, Graph, Namespace
from clueseval.clues.class_based import ClassBasedClue
from commons.utils import SemanticFilesLoader

class TestStats(unittest.TestCase):
    
    def _load_clues(self, semanticPath):
        sfl = SemanticFilesLoader(semanticPath)
        names = sfl.selectStations()
        graphs = {}
        sfl.loadGraphsJustOnce(names, graphs)
        
        clues = {}
        for node_name in graphs:
            if node_name not in ('ontology','ontology_expanded'):
                clues[node_name] = ClassBasedClue(graphs['ontology'])
                
                union = Graph()
                for g in graphs[node_name]:
                    for t in g.triples((None, None, None)):
                        union.add(t)
                        # arreglar lo de los namespaces en la union!
                   
                clues[node_name].parseGraph(union)
                clues[node_name].expand() # TODO mock expansion!
                
        return clues
    
    def _assert_candidates(self, expected_candidates, template, clues):
        for name, clue in clues.iteritems():
            if name in expected_candidates:
                self.assertTrue( clue.isCandidate(template), msg="%s expected to be a candidate for template %s"%(name, template) )
            else:
                self.assertFalse( clue.isCandidate(template), msg="%s not expected to be a candidate for template %s"%(name, template) )
    
    def test_isCandidate(self):
        clues = self._load_clues('../sample_files')
        
        SSN = Namespace('http://purl.oclc.org/NET/ssnx/ssn#')
        SSN_WEATHER = Namespace('http://knoesis.wright.edu/ssw/ont/weather.owl#')
        WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
        BIZKAI_STATION = Namespace('http://helheim.deusto.es/bizkaisense/resource/station/')
        DC = Namespace('http://purl.org/dc/elements/1.1/')
        
        # TEST
        templates = (
          # based on type
          (None, RDF.type, SSN_WEATHER.RainfallObservation), # in 43 nodes
          (None, WGS84.long, None), # 155 objects (long belongs to SpatialThing, Point is subclass of SpatialThing and does not have range)
          (None, SSN.observedProperty, None), # observedProperty's range is Observation, but we have just subclasses of Observation (e.g. TemperatureObservation)
                                              # knoesis defines its own observedProperty in SSN_OBSERV
          (BIZKAI_STATION.ABANTO, None, None), # given an instance, we cannot predict anything
          (None, DC.identifier, None),
        )
                
        self._assert_candidates( ('knoesis/ABMN6'), templates[0], clues )
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6'), templates[1], clues )
        self._assert_candidates( (), templates[2], clues ) # SSN subproperty de DUL
        self._assert_candidates( ('knoesis/A02','knoesis/ABMN6','bizkaisense/ALGORT','bizkaisense/ABANTO','aemet/08001','aemet/08002', 'luebeck/211','luebeck/300','morelab/aitor-almeida','morelab/aitor-gomez-goiri'), templates[3], clues )
        self._assert_candidates( (), templates[4], clues )

if __name__ == '__main__':
    unittest.main()
    