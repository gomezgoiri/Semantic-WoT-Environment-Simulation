import unittest
import urllib
from rdflib import URIRef
from rdflib.Literal import Literal, _XSD_NS
from netuse.triplespace.kernel import TripleSpace

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
        TripleSpace.__init__(self, None)
        
    def write(self, startAt):
        pass
    
    def query(self, template, startAt):
        pass

class KernelTestCase(unittest.TestCase):

    def test_fromTemplateToURL(self):
        k = ConcreteTS()
        self.assertEquals( "wildcards/*/*/*/", k.fromTemplateToURL((ANY, ANY, ANY)))
        
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/*/", k.fromTemplateToURL((SUBJECT, ANY, ANY)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/"+PREDICATE_QUOTED+"/*/", k.fromTemplateToURL((SUBJECT, PREDICATE, ANY)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+OBJECT_URI_QUOTED+"/", k.fromTemplateToURL((SUBJECT, ANY, OBJECT_URI)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/"+PREDICATE_QUOTED+"/"+OBJECT_URI_QUOTED+"/", k.fromTemplateToURL((SUBJECT, PREDICATE, OBJECT_URI)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+XSDBASE_URI_QUOTED+"float/21.11/", k.fromTemplateToURL((SUBJECT, ANY, OBJECT_NUMERIC_LITERAL)) )
        self.assertEquals( "wildcards/"+SUBJECT_QUOTED+"/*/"+XSDBASE_URI_QUOTED+"boolean/True/", k.fromTemplateToURL((SUBJECT, ANY, OBJECT_BOOLEAN_LITERAL)) )
        
        self.assertEquals( "wildcards/*/"+PREDICATE_QUOTED+"/*/", k.fromTemplateToURL((ANY, PREDICATE, ANY)) )
        self.assertEquals( "wildcards/*/"+PREDICATE_QUOTED+"/"+OBJECT_URI_QUOTED+"/", k.fromTemplateToURL((ANY, PREDICATE, OBJECT_URI)) )

        self.assertEquals( "wildcards/*/*/"+OBJECT_URI_QUOTED+"/", k.fromTemplateToURL((ANY, ANY, OBJECT_URI)))

if __name__ == '__main__':
    unittest.main()