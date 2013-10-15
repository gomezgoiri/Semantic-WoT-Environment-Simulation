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

import urllib
from rdflib import URIRef
from rdflib.Literal import _XSD_NS
from rdflib.Literal import Literal
from netuse.results import G


class URLUtils:
    @staticmethod
    def serialize_wildcard_to_URL(template):
        s = template[0]
        p = template[1]
        o = template[2]
        
        ret = 'wildcards/'
        
        ret += urllib.quote_plus(s) if s!=None else '*'
        ret += '/'
        ret += urllib.quote_plus(p) if p!=None else '*'
        ret += '/'
        
        if o is None:
            ret += '*/'
        elif isinstance(o, URIRef):
            ret += urllib.quote_plus(o)
            ret += '/'
        elif isinstance(o, Literal):
            ret += urllib.quote_plus(o.datatype)
            ret += '/'
            ret += urllib.quote(o) # or o.toPython()
            ret += '/'
            
        return ret
    
    @staticmethod
    def serialize_space_to_URL(space=G.defaultSpace):
        return 'spaces/' + urllib.quote_plus(space) + '/'
    
    @staticmethod
    def parse_wildcard_url(wildcard_url):
        # always starts with "wildcard/{template}"
        wildcard_tokens = wildcard_url[len('wildcards/'):].split('/')
        if len(wildcard_tokens)==4 and wildcard_tokens[3]!='': # With type
            xsd_type  = wildcard_tokens[2]
            str_value = wildcard_tokens[3]
            if xsd_type == 'xsd:float':
                o = Literal(str_value, datatype=_XSD_NS.float)
            elif xsd_type == 'xsd:double':
                o = Literal(str_value, datatype=_XSD_NS.double)
            elif xsd_type == 'xsd:int':
                o = Literal(str_value, datatype=_XSD_NS.int)
            elif xsd_type == 'xsd:integer':
                o = Literal(str_value, datatype=_XSD_NS.integer)
            elif xsd_type == 'xsd:long':
                o = Literal(str_value, datatype=_XSD_NS.long)
            elif xsd_type == 'xsd:boolean':
                o = Literal(str_value, datatype=_XSD_NS.boolean)
            elif xsd_type == 'xsd:string':
                o = Literal(str_value, datatype=_XSD_NS.string)
            else:
                raise Exception("Unsupported xsd type: %s" % xsd_type)
        elif len(wildcard_tokens) == 3 or (len(wildcard_tokens) == 4 and wildcard_tokens[3]==''): # With uri
            o = urllib.unquote(wildcard_tokens[2])
            if o == '*':
                o = None
            else: o = URIRef(o)
        else:
            raise Exception("Malformed wildcard: %s"  % wildcard_url)
    
        s = urllib.unquote(wildcard_tokens[0])
        if s == '*':
            s = None
        else: s = URIRef(s)
        
        p = urllib.unquote(wildcard_tokens[1])
        if p == '*':
            p = None
        else: p = URIRef(p)
    
        return (s, p, o)