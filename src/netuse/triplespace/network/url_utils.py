'''
Created on Oct 8, 2012

@author: tulvur
'''

import urllib
from rdflib import URIRef
from rdflib.Literal import Literal
from netuse.results import G


class URLUtils:
    @staticmethod
    def fromTemplateToURL(template):
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
    def fromSpaceToURL(space=G.defaultSpace):
        return 'spaces/' + urllib.quote_plus(space) + '/'