import unittest
import urllib
import StringIO
from mock import Mock
from rdflib.Literal import Literal
from rdflib.Literal import _XSD_NS
from rdflib.URIRef import URIRef
from rdflib.Graph import Graph
import netuse.triplespace.network.server as handlers
from netuse.triplespace.network.httpelements import HttpRequest
from netuse.triplespace.dataaccess.store import DataAccess

TRIPLES = Graph()
TRIPLES.add((URIRef('http://python'), URIRef('http://is'), URIRef('http://good'),))
TRIPLES.add((URIRef('http://java'), URIRef('http://is'), Literal('bad', datatype=_XSD_NS.string),))
# take into account that:
# >>> u = Literal('bad')
# >>> l = Literal('bad',datatype=_XSD_NS.string)
# >>> l
# rdflib.Literal(u'bad', datatype=rdflib.URIRef('http://www.w3.org/2001/XMLSchema#string'))
# >>> u
# rdflib.Literal(u'bad')


TRIPLES2 = Graph()
TRIPLES2.add((URIRef('http://temperature'), URIRef('http://temp_is'), Literal(5.5),))

#NT_GRAPH = TRIPLES.serialize(format="nt")
#NT_GRAPH2 = TRIPLES2.serialize(format="nt")

SPACE = 'tsc%3A%2F%2Ffoo%2Fbar'
UNQUOTED_SPACE = 'tsc://foo/bar'
GRAPH_URI = ""

PYTHON_URI = "http%3A%2F%2Fpython"
JAVA_URI   = "http%3A%2F%2Fjava"
IS_URI     = "http%3A%2F%2Fis"
GOOD_URI   = "http%3A%2F%2Fgood"


class SpacesHandlerTestCase(unittest.TestCase):

    def setUp(self):
        kernel = Mock()
        kernel.dataaccess = DataAccess(defaultSpace=UNQUOTED_SPACE)
        self.uri  = kernel.dataaccess.write(TRIPLES, UNQUOTED_SPACE)
        self.uri2 = kernel.dataaccess.write(TRIPLES2, UNQUOTED_SPACE)
        
        self.handler = handlers.CustomSimulationHandler(kernel)
        self.spaces_handler = handlers.SpacesHandler(kernel.dataaccess.stores)

    def test_list_spaces(self):
        code, response, _ = self.spaces_handler.process_spaces("")
        self.assertEquals(200, code)
        self.assertTrue(response.startswith("Space list"))

    def test_list_operations(self):
        code, response, _ = self.spaces_handler.process_spaces(SPACE)
        self.assertEquals(200, code)
        self.assertTrue(response.startswith("Operations with"))

        code, response, _ = self.spaces_handler.process_spaces("tsc%3A%2F%2Fdoes%2Fnot%2Fexist")
        self.assertEquals(404, code)
        self.assertTrue(response.startswith("Space not found"))

        code, response, _ = self.spaces_handler.process_spaces(SPACE + "/")
        self.assertEquals(200, code)
        self.assertTrue(response.startswith("Operations with"))

    def test_read_graph_empty(self):
        code, response, _ = self.spaces_handler.process_spaces(SPACE + "/graphs/", HttpRequest(-1, ''))
        self.assertEquals(200, code)
        self.assertTrue(response.startswith("Graph list"))

    def test_read_graph_uri_not_found(self):
        code, response, _ = self.spaces_handler.process_spaces(SPACE + "/graphs/this.does.not.exist")
        self.assertEquals(404, code)
        self.assertTrue(response.startswith("Graph not found"))

    def test_read_graph_uri(self):
        code, response, _ = self.spaces_handler.process_spaces(SPACE + "/graphs/" + urllib.quote(self.uri, ''))
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(TRIPLES.isomorphic(retGraph))

    def test_read_graph_wildcard_uris(self):
        self._test_read_graph_wildcard_uris_ok(PYTHON_URI, IS_URI, GOOD_URI)
        self._test_read_graph_wildcard_uris_ok(PYTHON_URI, IS_URI, '*')
        self._test_read_graph_wildcard_uris_ok(PYTHON_URI, '*',    GOOD_URI)
        self._test_read_graph_wildcard_uris_ok('*',        IS_URI, GOOD_URI)
        self._test_read_graph_wildcard_uris_ok('*',        IS_URI, '*')
        self._test_read_graph_wildcard_uris_ok(PYTHON_URI, '*',    '*')
        self._test_read_graph_wildcard_uris_ok('*',        '*',    GOOD_URI)
        self._test_read_graph_wildcard_uris_any('*',        '*',    '*')

        self._test_read_graph_wildcard_uris_fail(PYTHON_URI, IS_URI,     IS_URI)
        self._test_read_graph_wildcard_uris_fail('*',        '*',        IS_URI)
        self._test_read_graph_wildcard_uris_fail('*',        PYTHON_URI, '*')
        self._test_read_graph_wildcard_uris_fail(IS_URI,     '*',        '*')

    def _test_read_graph_wildcard_uris_ok(self, s, p, o):
        code, response, _ = self._test_read_graph_wildcard_uris(s,p,o)
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(TRIPLES.isomorphic(retGraph))

    def _test_read_graph_wildcard_uris_any(self, s, p, o):
        code, response, _ = self._test_read_graph_wildcard_uris(s,p,o)
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(TRIPLES.isomorphic(retGraph) or TRIPLES2.isomorphic(retGraph))

    def _test_read_graph_wildcard_uris_fail(self, s, p, o):
        code, response, _ = self._test_read_graph_wildcard_uris(s,p,o)
        self.assertEquals(404, code)
        self.assertTrue(response.startswith("Graph not found"))

    def _test_read_graph_wildcard_uris(self, s, p, o):
        code, response, content_type = self.spaces_handler.process_spaces(SPACE + "/graphs/wildcards/%s/%s/%s" % (s, p, o))
        self.assertTrue(code!=None)
        self.assertTrue(response!=None)
        return code, response, content_type

    def test_read_graph_wildcard_types(self):
        self._test_read_graph_wildcard_types_ok(JAVA_URI, IS_URI,   'xsd:string', "bad")
        self._test_read_graph_wildcard_types_ok(JAVA_URI, '*',      'xsd:string', "bad")
        self._test_read_graph_wildcard_types_ok('*',      IS_URI,   'xsd:string', "bad")
        self._test_read_graph_wildcard_types_ok('*',      '*',      'xsd:string', "bad")
        self._test_read_graph_wildcard_types_ok2('*',     '*',      'xsd:float',  5.5)

        self._test_read_graph_wildcard_types_fail(JAVA_URI, IS_URI, 'xsd:int',     "5")
        self._test_read_graph_wildcard_types_fail(JAVA_URI, IS_URI, 'xsd:integer', "5")
        self._test_read_graph_wildcard_types_fail('*',        '*',  'xsd:long',    "5")
        self._test_read_graph_wildcard_types_fail('*',        '*',  'xsd:float',   "5")
        self._test_read_graph_wildcard_types_fail('*',        '*',  'xsd:double',  "5")
        self._test_read_graph_wildcard_types_fail('*',        '*',  'xsd:boolean', "true")
        self.assertRaises(Exception, 
                    self._test_read_graph_wildcard_types_fail,
                    '*',        '*',  'xsd:foo',  "5") # xsd:foo does not exist

    def _test_read_graph_wildcard_types_ok(self, s, p, t, o):
        code, response, _ = self._test_read_graph_wildcard_types(s,p,t,o)
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(TRIPLES.isomorphic(retGraph))

    def _test_read_graph_wildcard_types_ok2(self, s, p, t, o):
        code, response, _ = self._test_read_graph_wildcard_types(s,p,t,o)
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(TRIPLES2.isomorphic(retGraph))

    def _test_read_graph_wildcard_types_fail(self, s, p, t, o):
        code, response, _ = self._test_read_graph_wildcard_types(s,p,t,o)
        self.assertEquals(404, code)
        self.assertTrue(response.startswith("Graph not found"))

    def _test_read_graph_wildcard_types(self, s, p, t, o):
        code, response, content_type = self.spaces_handler.process_spaces(SPACE + "/graphs/wildcards/%s/%s/%s/%s" % (s, p, t, o))
        self.assertTrue(code!=None)
        self.assertTrue(response!=None)
        return code, response, content_type
    
    def test_query_graph_wildcard_uris(self):
        PYTHON_URI_GRAPH = Graph()
        PYTHON_URI_GRAPH.add((URIRef('http://python'), URIRef('http://is'), URIRef('http://good'),))
        IS_URI_GRAPH = Graph()
        IS_URI_GRAPH.add((URIRef('http://python'), URIRef('http://is'), URIRef('http://good'),))
        IS_URI_GRAPH.add((URIRef('http://java'), URIRef('http://is'), Literal('bad', datatype=_XSD_NS.string),))
        ALL_GRAPH = Graph()
        ALL_GRAPH.add((URIRef('http://python'), URIRef('http://is'), URIRef('http://good'),))
        ALL_GRAPH.add((URIRef('http://java'), URIRef('http://is'), Literal('bad', datatype=_XSD_NS.string),))
        ALL_GRAPH.add((URIRef('http://temperature'), URIRef('http://temp_is'), Literal(5.5),))
        
        self._test_query_graph_wildcard_uris_ok(PYTHON_URI, IS_URI, GOOD_URI, PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok(PYTHON_URI, IS_URI, '*', PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok(PYTHON_URI, '*',    GOOD_URI, PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok('*',        IS_URI, GOOD_URI, PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok('*',        IS_URI, '*', IS_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok(PYTHON_URI, '*',    '*', PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok('*',        '*',    GOOD_URI, PYTHON_URI_GRAPH)
        self._test_query_graph_wildcard_uris_ok('*',        '*',    '*', ALL_GRAPH)

        self._test_query_graph_wildcard_types_fail(PYTHON_URI, IS_URI,     IS_URI)
        self._test_query_graph_wildcard_types_fail('*',        '*',        IS_URI)
        self._test_query_graph_wildcard_types_fail('*',        PYTHON_URI, '*')
        self._test_query_graph_wildcard_types_fail(IS_URI,     '*',        '*')

    def _test_query_graph_wildcard_uris_ok(self, s, p, o, expectedGraph):
        code, response, _ = self._test_query_graph_wildcard_uris(s,p,o)
        retGraph = Graph().parse(StringIO.StringIO(response),format="n3")
        self.assertEquals(200, code)
        self.assertTrue(expectedGraph.isomorphic(retGraph))
        
    def _test_query_graph_wildcard_types_fail(self, s, p, o):
        code, response, _ = self._test_query_graph_wildcard_uris(s,p,o)
        self.assertEquals(404, code)
        self.assertTrue(response.startswith("Graph not found"))
        
    def _test_query_graph_wildcard_uris(self, s, p, o):
        code, response, content_type = self.spaces_handler.process_spaces(SPACE + "/query/wildcards/%s/%s/%s" % (s, p, o))
        self.assertTrue(code!=None)
        self.assertTrue(response!=None)
        return code, response, content_type
    
    def test_write_graph(self):
        code, response, _ = self.spaces_handler.process_spaces(SPACE + "/graphs/", HttpRequest(-1, '', data=TRIPLES))
        self.assertEquals(200, code)
        self.assertTrue(response.startswith("The graph was successfully written"))

if __name__ == '__main__':
    unittest.main()
