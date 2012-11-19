'''
Created on Oct 26, 2012

@author: tulvur
'''

import json
import string
import random
import sqlite3
from tempfile import mkstemp
from clueseval.clues.storage.abstract_store import AbstractStore, AggregationClueUtils
from clueseval.clues.parent_clue import Clue
from clueseval.clues.node_attached import ClueWithNode
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue

# Note that currently just predicate-based clues' persistent store has been implemented.
class SQLiteClueStore(AbstractStore):
    SCHEMAS_TABLE = "schemas"
    PREDICATES_TABLE = "predicates"
    CLASSES_TABLE = "classes"
    
    _INSERT_SCHEMA = "insert into %s values (?,?)"%(SCHEMAS_TABLE)
    _INSERT_PREDICATE = "insert into %s values (?,?,?)"%(PREDICATES_TABLE)
    _INSERT_CLASSES = "insert into %s values (?,?,?)"%(CLASSES_TABLE)
    
    _SELECT_SCHEMA = "select * from " + SCHEMAS_TABLE    
    _SELECT_PREDICATE = "select * from " + PREDICATES_TABLE
    
    def __init__(self, database_name=None, database_path=None, tipe=None):
        db_path = database_path if database_path is None or database_path.endswith("/") else database_path + "/"
        
        if database_name is None:
            self.db_file = mkstemp(suffix=".db", dir=db_path)[1]
        else:
            self.db_file = database_name
        self.type = PredicateBasedClue.ID() # right now, just predicate-based clues have been implemented in SQLite store
        
    def start(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cur = self.conn.cursor()
        # Simplification, we always create the 3 tables
        self.cur.execute("""create table if not exists %s (
                            name VARCHAR(255) PRIMARY KEY NOT NULL,
                            uri VARCHAR(255) NOT NULL)
                        """%(SQLiteClueStore.SCHEMAS_TABLE)
                        )
        self.cur.execute("""create table if not exists %s (
                            node VARCHAR(255) NOT NULL,
                            prefix VARCHAR(255) NOT NULL,
                            ending VARCHAR(255) NOT NULL,
                            PRIMARY KEY (node, prefix, ending) )
                         """%(SQLiteClueStore.PREDICATES_TABLE)
                         )
        self.cur.execute("""create table if not exists %s (
                            node VARCHAR(255) NOT NULL,
                            prefix VARCHAR(255) NOT NULL,
                            ending VARCHAR(255) NOT NULL,
                            PRIMARY KEY (node, prefix, ending) )
                         """%(SQLiteClueStore.CLASSES_TABLE)
                         )
        self.conn.commit()
    
    def stop(self):
        self.cur.close()
        self.conn.close()
        
    def _get_schema_name_for_URI(self, URI):
        '''
            If the URI of the schema already exists in the table returns its name.
            
            Otherwise, returns 'None'.
        '''
        cur = self.conn.execute(SQLiteClueStore._SELECT_SCHEMA + " where uri=:uri", {"uri": URI}) 
        stored_name = cur.fetchone()
        return None if stored_name is None else stored_name[0]
    
    # from http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):        
        return ''.join(random.choice(chars) for _ in range(size))
    
    def _get_estimated_size(self, existing_elements):
            # len(string.ascii_uppercase + string.digits) == 36
            # len < 36: size=1
            # len < 36 + 36*36: size=2 (36*36 with 2 slots, plus 36 created with 1 slot)
            # len < 36 + 36*36 + 36*36*36: size=3
            # But I will simplify: elements==n => size = n/36 till it "n" is 0
                        
            needed_size = 1
            new_ids_per_size_unit = len(string.ascii_uppercase + string.digits)
            while existing_elements >= new_ids_per_size_unit :
                existing_elements /= new_ids_per_size_unit
                needed_size += 1
            return needed_size
    
    def _get_another_schema_name_if_collisions(self, name_to_check):
        '''
            Checks if another prefix has the same name.
            
            If so, it proposes a name that does not exist in the table returning it.
        '''
        # Another schema name starts with "name_to_check"?
        cur = self.conn.execute(SQLiteClueStore._SELECT_SCHEMA + " where name like '%s%%'"%(name_to_check))
        similar_names = [name for name, _ in cur.fetchall()] # names with the same root
        
        if not similar_names: # empty list => does not collision
            return name_to_check
        else:
            # Highly inefficient approach!
            size = self._get_estimated_size( len(similar_names) )
            proposed_name = name_to_check + self.id_generator( size=size )
            while proposed_name in similar_names:
                proposed_name = name_to_check + self.id_generator( size=size )
            
            return proposed_name
            
    def _just_inserts_schema(self, name, URI): # isolated in its own method for testing purposes
        self.conn.execute(SQLiteClueStore._INSERT_SCHEMA, (name, URI))
        self.conn.commit()
        
    def _insert_schema(self, name, URI):
        '''
            Insert schema (name, URI) in the proper table if not exists.
            
            It may change the name to avoid collisions or give them a proper name.
            Therefore this method will return the final name adopted by this prefix.
        '''
        existing_name = self._get_schema_name_for_URI(URI)
        
        if existing_name is None: # Inserts the one passed on the parameters
            # Avoid  "_number" like names created by rdflib.
            if name.startswith("_"):
                name = self.generate_prefix_name(URI)
            
            name = self._get_another_schema_name_if_collisions(name)
            self._just_inserts_schema(name, URI)
            
            return name
        else:
            return existing_name
    
    def get_schemas(self):
        schemas = []
        cur = self.conn.execute(SQLiteClueStore._SELECT_SCHEMA)
        row = cur.fetchone()
        while row is not None:
            schemas.append(row)
            row = cur.fetchone()
        return schemas
            
    def get_predicates(self):
        predicates = {}
        cur = self.conn.execute(SQLiteClueStore._SELECT_PREDICATE)
        
        row = cur.fetchone()
        while row is not None:
            node = row[0]
            prefix = row[1]
            ending = row[2]
            
            if node not in predicates:
                predicates[node] = {}
            if prefix not in predicates[node]:
                predicates[node][prefix] = []
            
            predicates[node][prefix].append(ending)
            row = cur.fetchone()
        return predicates
    
    def toJson(self):
        dictio = {}
        
        if self.type is not None: # if the type is not set, we return an empty dictionary
            dictio[Clue.ID_P()] = self.type
            
            if self.type==SchemaBasedClue.ID():
                raise NotImplementedError()
            elif self.type==PredicateBasedClue.ID():
                dictio[SchemaBasedClue._SCHEMA()] = self.get_schemas()
                dictio[PredicateBasedClue._PREDICATE()] = self.get_predicates()
            elif self.type==PredicateBasedClue.ID():
                raise NotImplementedError()
                    
        return AggregationClueUtils.toJson(dictio)
    
    def reset_all(self):
        self.conn.execute("delete from " + SQLiteClueStore.SCHEMAS_TABLE)
        self.conn.execute("delete from " + SQLiteClueStore.PREDICATES_TABLE)
        self.conn.execute("delete from " + SQLiteClueStore.CLASSES_TABLE)
        self.conn.commit()
    
    def fromJson(self, json_str): # using transactions
        # Overrides previously stored clues
        self.reset_all()
        
        dictio = AggregationClueUtils.fromJson(json_str)
        
        if dictio: # if the dictionary is empty, we don't do anything
            self.type = dictio[Clue.ID_P()]
            
            if self.type==SchemaBasedClue.ID():
                raise NotImplementedError()
            elif self.type==PredicateBasedClue.ID():
                mappings = {}
                for name, URI in dictio[SchemaBasedClue._SCHEMA()]:
                    stored_name = self._insert_schema(name, URI)
                    if stored_name is not name:
                        mappings[name] = stored_name
                
                with self.conn:
                    for node_name, uris in dictio[PredicateBasedClue._PREDICATE()].iteritems():
                        for prefix, endings in uris.iteritems():
                            actual_prefix = prefix if prefix not in mappings else mappings[prefix]
                            self.conn.executemany( SQLiteClueStore._INSERT_PREDICATE, [(node_name, actual_prefix, ending) for ending in endings] )
            elif self.type==ClassBasedClue.ID():
                raise NotImplementedError()
    
    # TODO delete schemas if they are no longer used?
    def reset_preficates_for_node(self, node_name):
        self.conn.execute( "delete from %s where node='%s'"%(SQLiteClueStore.PREDICATES_TABLE, node_name) )
        self.conn.commit()
    
    def add_clue(self, node_name, clue_json):
        self.reset_preficates_for_node(node_name)
        dictio = json.loads(clue_json)
        
        clue_type = dictio[Clue.ID_P()]
        if self.type is None:
            self.type = clue_type
        else:
            if clue_type is not self.type:
                raise Exception("This store only accepts clues of the type %d"%(self.type))
        
        if self.type==SchemaBasedClue.ID():
            raise NotImplementedError()
        elif self.type==PredicateBasedClue.ID():
            mappings = {}
            dictio = dictio[ClueWithNode.CLUE()]
            for name, URI in dictio[SchemaBasedClue._SCHEMA()]:
                stored_name = self._insert_schema(name, URI)
                if stored_name is not name:
                    mappings[name] = stored_name
            with self.conn:
                for prefix, endings in dictio[PredicateBasedClue._PREDICATE()].iteritems():
                    actual_prefix = prefix if prefix not in mappings else mappings[prefix]
                    self.conn.executemany( SQLiteClueStore._INSERT_PREDICATE, [(node_name, actual_prefix, ending) for ending in endings] )
        elif self.type==ClassBasedClue.ID():
            raise NotImplementedError()
    
    def _get_domain(self, uri):
        not_domain_from = uri.find("/", uri.find("://")+len("://")+1) # not found==-1
        if not_domain_from==-1:
            not_domain_from = uri.find("#") # not found==-1
            if not_domain_from==-1:
                return uri
        return uri[:not_domain_from]
    
    def _get_prefixes_for(self, uri):
        domain = self._get_domain(uri)
        # really simple filter by domain
        # if there are many prefixes with the same URI, it won't be so useful, but I assume that is unlikely
        cur = self.conn.execute("select * from %s where uri like '%s%%'"%(SQLiteClueStore.SCHEMAS_TABLE, domain))
        
        prefixes = []
        row = cur.fetchone()
        while row is not None:
            if uri.startswith(row[1]):
                prefixes.append(row)
            row = cur.fetchone()
        
        return prefixes
    
        
    def _get_nodes_with_predicate(self, prefix, uri_ending):
        cur = self.conn.execute(SQLiteClueStore._SELECT_PREDICATE + " where prefix='%s' and ending='%s'"%(prefix, uri_ending))
        
        nodes = set()
        row = cur.fetchone()
        while row is not None:
            nodes.add(row[0])
            row = cur.fetchone()
        
        return nodes
    
    # return the nodes which may have relevant data for a given query
    def get_query_candidates(self, template):
        candidates = set()
        prefixes = self._get_prefixes_for(template[1])
        
        for name, uri in prefixes: # usually just 1 prefix matching, but just in case...
            uri_ending = template[1][len(uri):]
            candidates |= self._get_nodes_with_predicate(name, uri_ending)
        
        return candidates