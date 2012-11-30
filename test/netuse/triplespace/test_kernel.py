import unittest
import urllib
from rdflib import URIRef
from rdflib.Literal import Literal, _XSD_NS
from netuse.triplespace.kernel import TripleSpace
from netuse.triplespace.network.url_utils import URLUtils

ANY = None
SUBJECT = URIRef("http://subject")
SUBJECT_QUOTED = urllib.quote_plus(str(SUBJECT))
PREDICATE = URIRef("http://predicate")
PREDICATE_QUOTED = urllib.quote_plus(str(PREDICATE))
OBJECT_URI = URIRef("http://object")
OBJECT_URI_QUOTED = urllib.quote_plus(str(OBJECT_URI))
OBJECT_NUMERIC_LITERAL = Literal(21.11)
# Warning: Boolean literal in 2.4 -> http://code.google.com/p/rdflib/issues/detail?id=88
OBJECT_BOOLEAN_LITERAL = Literal(True, datatype=_XSD_NS.boolean)
XSDBASE_URI_QUOTED = 'http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23' 

class ConcreteTS(TripleSpace):
    def __init__(self):
        super(ConcreteTS, self).__init__(None, None)
        
    def write(self, startAt):
        pass
    
    def query(self, template, startAt):
        pass

class KernelTestCase(unittest.TestCase):

    def test_fromTemplateToURL(self):
        k = ConcreteTS()
        self.assertEquals( "wildcards/*/*/*/", URLUtils.serialize_wildcard_to_URL((ANY, ANY, ANY)))
        
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/*/", URLUtils.serialize_wildcard_to_URL((SUBJECT, ANY, ANY)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/"+PREDICATE_QUOTED+"/*/", URLUtils.serialize_wildcard_to_URL((SUBJECT, PREDICATE, ANY)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+OBJECT_URI_QUOTED+"/", URLUtils.serialize_wildcard_to_URL((SUBJECT, ANY, OBJECT_URI)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/"+PREDICATE_QUOTED+"/"+OBJECT_URI_QUOTED+"/", URLUtils.serialize_wildcard_to_URL((SUBJECT, PREDICATE, OBJECT_URI)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+XSDBASE_URI_QUOTED+"float/21.11/", URLUtils.serialize_wildcard_to_URL((SUBJECT, ANY, OBJECT_NUMERIC_LITERAL)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+XSDBASE_URI_QUOTED+"boolean/True/", URLUtils.serialize_wildcard_to_URL((SUBJECT, ANY, OBJECT_BOOLEAN_LITERAL)) )
        
        self.assertEquals( "wildcards/*/"+PREDICATE_QUOTED+"/*/", URLUtils.serialize_wildcard_to_URL((ANY, PREDICATE, ANY)) )
        self.assertEquals( "wildcards/*/"+PREDICATE_QUOTED+"/"+OBJECT_URI_QUOTED+"/", URLUtils.serialize_wildcard_to_URL((ANY, PREDICATE, OBJECT_URI)) )

        self.assertEquals( "wildcards/*/*/"+OBJECT_URI_QUOTED+"/", URLUtils.serialize_wildcard_to_URL((ANY, ANY, OBJECT_URI)))

if __name__ == '__main__':
    unittest.main()