'''
Created on Oct 26, 2012

@author: tulvur
'''
import json
import re
from abc import abstractmethod, ABCMeta
from clueseval.clues.parent_clue import Clue
from clueseval.clues.schema_based import SchemaBasedClue
from clueseval.clues.predicate_based import PredicateBasedClue
from clueseval.clues.class_based import ClassBasedClue

class AggregationClueUtils(object):
    """
    {
      "i": 1,
      "s": [
        ["dc", "http://purl.org/dc/elements/1.1/"],
        ["dul", "http://www.loa.istc.cnr.it/ontologies/DUL.owl#"],
        ["ssn", "http://purl.oclc.org/NET/ssnx/ssn#"]
          ],
      "p": {
        "node1": {
          "ssn": ["observedBy", "observationResult"],
          "dul": ["isClassifiedBy"]
        },
        "node0": {
          "ssn": ["observes"],
          "dc": ["description"]
    } } }
    """
    
    @staticmethod
    def validate(dictionary):
        if Clue.ID_P() in dictionary:
            if dictionary[Clue.ID_P()] is SchemaBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary
            elif dictionary[Clue.ID_P()] is PredicateBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary and PredicateBasedClue._PREDICATE() in dictionary
            elif dictionary[Clue.ID_P()] is ClassBasedClue.ID():
                return SchemaBasedClue._SCHEMA() in dictionary and ClassBasedClue._CLASS() in dictionary
        return False
    
    @staticmethod
    def toJson(dictionary):
        if dictionary and not AggregationClueUtils.validate(dictionary):
            raise Exception("Malformed clue." + str(dictionary))
        return json.dumps(dictionary)
    
    @staticmethod
    def fromJson(json_str):
        dictionary = json.loads(json_str)
        if dictionary and not AggregationClueUtils.validate(dictionary):
            raise Exception("Malformed clue.")
        return dictionary


class AbstractStore(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    def _get_n_most_representative_chars(self, word, n):
        result = ""
        prog = re.compile(r"""
                            ^[^a-zA-Z]*  # Ignore not alphabetic chars
                            ([a-z]?)     # (possibly) take the first alphabetic lower char
                            """, re.X ) #"^\d*([a-zA-Z])[a-z\d]*(?:([A-Z]+)[a-z\d]*)+$")
        for match in prog.findall(word):
            result += match
        
        # takes the uppercase chars
        prog = re.compile(r"([A-Z])")
        for match in prog.findall(word):
            result += match
        
        if len(result)==n:
            return result
        elif len(result)>n:
            return result[:n]
        else:
            # In case not enough chars were extracted...
            
            # We take the lowercase chars after the last uppercase chars
            prog = re.compile(r"""
                                [A-Z]      # ignore LAST uppercase
                                ( [a-z]+ ) # take the lowercase chars after
                                $          # the string finishes here
                                """, re.X)
            matches = prog.findall(word)
            
            if matches:
                for match in matches:
                    result += match
            else:
                # If no uppercase was found or no lowercase after the last uppercase...
                prog = re.compile(r"""
                                    ^ [^a-zA-Z]*  # Ignore not alphabetic chars
                                      [a-zA-Z]    # Ignore the first alphabetic chat (already considered in previous compile)
                                                  # Upper or lowercase
                                      (?:
                                           ([a-z]+ ) # take the first lowercase chars
                                            [^a-z]*  # Ignore the rest
                                      )
                                    """, re.X)                
                for match in prog.findall(word):
                    result += match
            
            needed_chars = n - len(result)
            if needed_chars<=0:
                return result[:n]
            else:
                # fill the following chars with "x"s
                return result + ("x")*needed_chars
    
    def generate_prefix_name(self, uri, length_of_prefix=3):
        # http://something/sth2/ontologyname#something like URIs
        prog = re.compile(r"""
                            ^\w+://           # Starts with "protocol://" like chars
                            [./\w]+          # followed by some chars
                            / [^a-zA-Z]*     # After the last slash, ignore first not alphabetic chars
                            ( [a-zA-Z_\-]+ ) # Takes following chars (including alphabetic)
                            (?: \.\w+ )?     # Ignore ontology extension (e.g. .owl)
                            \#               # We finish in with sharp
                           """, re.X) # "-" and "_" ignored when they are before alphabetic chars
        matched = prog.match(uri)
        if matched:
            return self._get_n_most_representative_chars(matched.group(1), length_of_prefix)
        
        # http://something/sth2/sth3/sth4 like URIs
        prog = re.compile(r"""
                            ^\w+://           # Starts with "protocol://" like chars
                            [./\w]+           # followed by some chars
                            / ( [a-zA-Z]      # Find the last slash followed by an alphabetic char 
                                .* )          # Take all the chars after that slash
                            (?:               # Possibly...
                              (?:
                                  / |         # ignore last slash or
                                  / [^a-zA-Z] # ignore following chars between slashes
                                    .*
                                )
                            )?
                           """, re.X) # "-" and "_" ignored when they are before alphabetic chars
        matched = prog.match(uri)
        if matched:
            return self._get_n_most_representative_chars(matched.group(1), length_of_prefix)
        
        else_prefix = "prefix"
        else_prefix = else_prefix[:length_of_prefix] if len(else_prefix)>=length_of_prefix else else_prefix + ("x")*length_of_prefix
        return else_prefix
        
        
    @abstractmethod
    def add_clue(self, node_name, clue_json):
        pass
    
    @abstractmethod
    def toJson(self):
        pass
    
    @abstractmethod
    def fromJson(self, json_str):
        pass
    
    @abstractmethod
    def get_query_candidates(self, template):
        pass