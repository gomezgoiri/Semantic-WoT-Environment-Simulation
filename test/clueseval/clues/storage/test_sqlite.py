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

import os
import unittest
from rdflib import Namespace
from clueseval.clues.node_attached import ClueWithNode
from clueseval.clues.storage.sqlite import SQLiteClueStore
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue

SSN_SCHEMA = 'ssn'
DC_SCHEMA = 'dc'
DUL_SCHEMA = 'dul'

namespaces = { SSN_SCHEMA: Namespace('http://purl.oclc.org/NET/ssnx/ssn#'),
               DC_SCHEMA: Namespace('http://purl.org/dc/elements/1.1/'),
               DUL_SCHEMA: Namespace('http://www.loa.istc.cnr.it/ontologies/DUL.owl#') }


# TODO test aggregations of schema-based and class-based clues
class TestClueAggregation(unittest.TestCase):
        
    def setUp(self):
        self.clue_store = SQLiteClueStore()
        self.clue_store.start()
        
        clue = PredicateBasedClue()
        clue.schemas = [ ( SSN_SCHEMA, namespaces[SSN_SCHEMA][''] ),
                         ( DC_SCHEMA, namespaces[DC_SCHEMA][''] ) ]
        clue.predicates = [ namespaces[SSN_SCHEMA]['observedBy'],
                            namespaces[DC_SCHEMA]['description'] ]
        self.clue_store.add_clue('node0', ClueWithNode('XXX', clue).toJson())
        
        clue = PredicateBasedClue()
        clue.schemas = [ ( SSN_SCHEMA, namespaces[SSN_SCHEMA][''] ),
                         ( DUL_SCHEMA, namespaces[DUL_SCHEMA][''] ) ]
        clue.predicates = [ namespaces[SSN_SCHEMA]['observedBy'],
                            namespaces[SSN_SCHEMA]['observationResult'],
                            namespaces[DUL_SCHEMA]['isClassifiedBy'] ]
        self.clue_store.add_clue('node1', ClueWithNode('XXX', clue).toJson())
    
    def tearDown(self):
        self.clue_store.stop()
        os.remove( self.clue_store.db_file )
    
    def test_get_estimated_size(self):
        self.assertEquals( 1, self.clue_store._get_estimated_size(0) )
        self.assertEquals( 1, self.clue_store._get_estimated_size(35) )
        self.assertEquals( 2, self.clue_store._get_estimated_size(36) )
        self.assertEquals( 2, self.clue_store._get_estimated_size(36*36-1) )
        self.assertEquals( 4, self.clue_store._get_estimated_size(36*36*36*36-1) )
        self.assertEquals( 5, self.clue_store._get_estimated_size(36*36*36*36) )

    def test_get_another_schema_name_if_collisions(self):
        schemas = []
        schemas.append( ("prefix", "http://superuri/myont/") )
        for i in range(3):
            schemas.append( ("prefix%d"%(i), "http://superuri/myont/%d"%(i)) )
        
        for schema in schemas:
            self.clue_store._just_inserts_schema(schema[0], schema[1])
        
        proposed = self.clue_store._get_another_schema_name_if_collisions("prefix")
        self.assertTrue( proposed not in schemas )
        
        proposed = self.clue_store._get_another_schema_name_if_collisions("profix") # does not exist
        self.assertEquals( "profix", proposed )
    
    def test_get_schemas(self):
        schemas = self.clue_store.get_schemas()
        self.assertEquals( 3, len(schemas) )
        self.assertTrue( ( SSN_SCHEMA, str( namespaces[SSN_SCHEMA][''] ) ) in schemas )
        self.assertTrue( ( DC_SCHEMA, str( namespaces[DC_SCHEMA][''] ) ) in schemas )
        self.assertTrue( ( DUL_SCHEMA, str( namespaces[DUL_SCHEMA][''] ) ) in schemas )

    def test_just_inserts_schema(self):
        # initial condition already tested on test_get_schemas        
        self.clue_store._just_inserts_schema("pr1", "http://URI1")
        schemas = self.clue_store.get_schemas()
        
        self.assertEquals( 4, len(schemas) )
        self.assertTrue( ( "pr1", "http://URI1" ) in schemas )

    def test_insert_schema(self):
        self.clue_store._just_inserts_schema("pr1", "http://URI1")
        
        # URI already exists with another prefix name
        new_name = self.clue_store._insert_schema("pr3", "http://URI1")
        self.assertEquals( "pr1", new_name )
        
        # prefix name already exist
        new_name = self.clue_store._insert_schema("pr1", "http://URI2")
        self.assertNotEquals( "pr1", new_name )
        
        # Unexisting prefix name or URI, just inserts it
        new_name = self.clue_store._insert_schema("pr4", "http://URI4")
        self.assertEquals( "pr4", new_name )
    
    def test_get_predicates(self):
        predicates = self.clue_store.get_predicates()
        self.assertTrue( predicates['node0'][SSN_SCHEMA], 'observedBy')
        self.assertTrue( predicates['node0'][DC_SCHEMA], 'description')
        self.assertTrue( predicates['node1'][SSN_SCHEMA], 'observedBy')
        self.assertTrue( predicates['node1'][SSN_SCHEMA], 'observationResult')
        self.assertTrue( predicates['node1'][DUL_SCHEMA], 'isClassifiedBy')
        
    def _assert_predicate_in_original_clues(self, node, parsed_clue, original_clue):
        # if not optimized, parsed may contain more schemas than really used in that clue
        # In other words, all original clues' schemas exist in parsed clues, but not viceversa.
        for sch in original_clue.schemas:
            self.assertTrue(sch in parsed_clue.schemas)
        
        for predicate in parsed_clue.predicates:
            self.assertTrue(predicate in original_clue.predicates)
    
    
    def test_add_incompatible_type_of_clue(self):
        clue = ClassBasedClue(None)
        clue.schemas = [ ( SSN_SCHEMA, namespaces[SSN_SCHEMA][''] ),
                         ( DUL_SCHEMA, namespaces[DUL_SCHEMA][''] ) ]
        clue.classes = [namespaces[SSN_SCHEMA]['ClassA'],
                        namespaces[SSN_SCHEMA]['ClassB'],
                        namespaces[DUL_SCHEMA]['ClassC'] ]
        try:
            self.clue_store.add_clue('node2', ClueWithNode('XXX', clue).toJSON())
            self.fail()
        except:
            pass
        
    def test_get_domain(self):
        domain = "http://www.ont.org"
        self.assertEquals( domain, self.clue_store._get_domain( domain + "/ont1/os" ) )
        self.assertEquals( domain, self.clue_store._get_domain( domain + "#eoe" ) )
        self.assertEquals( domain, self.clue_store._get_domain( domain ) )
    
    def test_get_prefixes_for(self):
        uri = namespaces[SSN_SCHEMA]['ClassA']
        prefixes = self.clue_store._get_prefixes_for(uri)
        self.assertEquals( 1, len(prefixes) )
        self.assertEquals( prefixes[0][0], SSN_SCHEMA )
        self.assertEquals( prefixes[0][1], str(namespaces[SSN_SCHEMA]['']) )
        
    def test_get_nodes_with_predicate(self):
        nodes = self.clue_store._get_nodes_with_predicate(SSN_SCHEMA, "notExisting")
        self.assertEquals(0, len(nodes))
        
        nodes = self.clue_store._get_nodes_with_predicate(DUL_SCHEMA, "isClassifiedBy")
        self.assertEquals(1, len(nodes))
        self.assertItemsEqual( ('node1',), nodes)
        
        nodes = self.clue_store._get_nodes_with_predicate(SSN_SCHEMA, "observedBy")
        self.assertEquals(2, len(nodes))
        self.assertItemsEqual( ('node0', 'node1'), nodes)
    
    def assert_equal_predicates_for_node(self, expected, tested): # checks the dictionary
        for schm_name, predicates in tested.iteritems():
            self.assertTrue( expected.has_key(schm_name) )
            self.assertItemsEqual( expected[schm_name], predicates )
    
    def assert_equal_predicates(self, expected, tested): # checks the dictionary
        self.assertEquals(len(expected), len(tested))
        for nodename, predicates_by_schemas  in tested.iteritems():
            self.assertTrue( expected.has_key(nodename) )
            self.assertEquals( len(expected[nodename]), len(predicates_by_schemas) )
            self.assert_equal_predicates_for_node( expected[nodename], predicates_by_schemas )
    
    def assert_equal_clue_stores(self, expected_cs, test_cs):
        self.assertEquals(expected_cs.type, test_cs.type)
        
        expected_schms = expected_cs.get_schemas()
        test_schms = test_cs.get_schemas()
        self.assertItemsEqual(expected_schms, test_schms)
                
        expected_preds = expected_cs.get_predicates()
        test_preds = test_cs.get_predicates()
        self.assert_equal_predicates(expected_preds, test_preds)
    
    def test_parseJson_predicates(self):
        clue_store2 = SQLiteClueStore()
        clue_store2.start()
        
        try:
            clue_store2.fromJson(self.clue_store.toJson())
            self.assert_equal_clue_stores(self.clue_store, clue_store2)
            
            clue_store2.fromJson(self.clue_store.toJson()) # importing a 2nd time, should override first changes
            self.assert_equal_clue_stores(self.clue_store, clue_store2)
        finally:
            clue_store2.stop()
    
    def test_add_clue(self):
        clue = PredicateBasedClue()
        schema = "http://fakeuri/"
        namespace = Namespace(schema)
        clue.schemas = [ ( "fk", namespace ), ]
        clue.predicates = [ namespace['predA'],
                            namespace['predB'],
                            namespace['predC'] ]
        
        # should override any existing clue (added in the setUp()) for the node1
        self.clue_store.add_clue('node1', ClueWithNode('XXX', clue).toJson())
        
        preds = self.clue_store.get_predicates()
        self.assert_equal_predicates_for_node( { "fk": ['pred'+chr(i) for i in range(ord('A'), ord('C')+1)] }, preds['node1'] )
    
    def test_get_query_candidates(self):
        candidates = self.clue_store.get_query_candidates( (None, 'http://strangeURI', None) )
        self.assertEquals(0, len(candidates))
                
        candidates = self.clue_store.get_query_candidates( (None, namespaces[DUL_SCHEMA]["isClassifiedBy"], None) )
        self.assertEquals(1, len(candidates))
        self.assertItemsEqual( ('node1',), candidates)
        
        candidates = self.clue_store.get_query_candidates( (None, namespaces[SSN_SCHEMA]["observedBy"], None) )
        self.assertEquals(2, len(candidates))
        self.assertItemsEqual( ('node0', 'node1'), candidates)
        
    def test_get_query_candidates_with_none_predicate(self):
        candidates = self.clue_store.get_query_candidates( (None, None, None) )
        self.assertEquals(2, len(candidates))
        self.assertItemsEqual( ('node0', 'node1'), candidates)
    
    def test_persistence(self):
        clue_store2 = SQLiteClueStore(database_name=self.clue_store.db_file)
        clue_store2.start()
        
        try:
            self.assert_equal_clue_stores(self.clue_store, clue_store2)
        finally:
            clue_store2.stop()


if __name__ == '__main__':
    unittest.main()