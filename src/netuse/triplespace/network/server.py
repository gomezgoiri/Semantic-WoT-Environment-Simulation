'''
Created on Dec 13, 2011

@author: tulvur
'''
import traceback
import urllib
from rdflib import Literal, URIRef
from rdflib.Literal import _XSD_NS

from netuse.triplespace.network.httpelements import HttpResponse

class SpacesHandler(object):
    def __init__(self, stores):
        self.stores      = stores

    def process_spaces(self, spaces_path, request=None):
        # Simple list of spaces:
        if spaces_path == '':
            return (200, """Space list (not implemented)""", 'text/html')

        pos = spaces_path.find('/') 
        if pos >= 0:
            quoted_space      = spaces_path[:pos]
        else:
            quoted_space      = spaces_path

        space = urllib.unquote(quoted_space)
        if not space in self.stores:
            return (404, """Space not found""", 'text/html')

        space_operation = spaces_path[len(quoted_space) + 1:] # + 1 for the last '/'
        if space_operation == '':
            return (200, """Operations with space (not implemented)""", 'text/html')

        store = self.stores[space]

        return self.process_space_operation(store, space_operation, request)

    def process_space_operation(self, store, operation, request):
        if operation.startswith('graphs'):
            graph_operation = operation[len('graphs/'):]
            return self.process_graph_operation(store, graph_operation, request)
        if operation.startswith('query'):
            graph_operation = operation[len('query/'):]
            return self.process_query_operation(store, graph_operation)
        if operation.startswith('gossip'):
            graph_operation = operation[len('gossip/'):]
            return self.process_gossip_operation(store)
        
        return (404, """Method not found""", 'text/html')
    
    def process_graph_operation(self, store, graph_operation, request):
        if graph_operation == '':
            method = request.get_method()
            if method=='GET':
                return (200, """Graph list (not implemented)""", 'text/html')
            elif method=='POST':
                actual_graph = request.get_data() # Graph().parse(StringIO.StringIO(request.get_data()), format='n3')
                store.write(actual_graph)
                return (200, """The graph was successfully written""", 'text/html')
            # cannot be another method, urllib2 does not use them
        
        if graph_operation.find('/') >= 0:
            quoted_graph_uri = graph_operation[:graph_operation.find('/')]
        else:
            quoted_graph_uri = graph_operation

        # Retrieve the graph
        if quoted_graph_uri == 'wildcards':
            wildcard_str = graph_operation[len('wildcards/'):]
            wildcard = self.parse_wildcard(wildcard_str)
            graph = store.read_wildcard(*wildcard)
        else: # We have an URI
            graph_uri = urllib.unquote(quoted_graph_uri)
            graph = store.read_uri(graph_uri)

        return self.process_graph(graph)
    
    def process_query_operation(self, store, graph_operation):
        if graph_operation == '':
            return (200, """Graph list (not implemented)""", 'text/html')
        
        if graph_operation.find('/') >= 0:
            quoted_graph_uri = graph_operation[:graph_operation.find('/')]
        else:
            quoted_graph_uri = graph_operation
        
        # Retrieve the graph
        if quoted_graph_uri == 'wildcards':
            wildcard_str = graph_operation[len('wildcards/'):]
            wildcard = self.parse_wildcard(wildcard_str)
            graph = store.query_wildcard(*wildcard)
            return self.process_graph(graph)
        
        return (404, """Method not found""", 'text/html')
    
    def process_gossip_operation(self, store):
        gossip = store.get_gossip()
        if gossip==None:
            return (404, """Nothing to gossip""", 'text/html')
        else:
            return (200, gossip.serializeToJson(), 'application/json')

    def parse_wildcard(self, wildcard_str):
        wildcard_tokens = wildcard_str.split('/')
        if len(wildcard_tokens) == 4 and wildcard_tokens[3]!='': # With type
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
            raise Exception("Malformed wildcard: %s"  % wildcard_str)

        s = urllib.unquote(wildcard_tokens[0])
        if s == '*':
            s = None
        else: s = URIRef(s)
        
        p = urllib.unquote(wildcard_tokens[1])
        if p == '*':
            p = None
        else: p = URIRef(p)

        return (s, p, o)

    def process_graph(self, graph):
        if graph is None:
            return (404, """Graph not found""", 'text/html')
        
        ntriples = graph.serialize(format='n3') # or nt, n3, owl...

        return (200, ntriples, 'text/n3') # text/n-triples, text/n3


class WhitepageHandler(object):
    def __init__(self, whitepage):
        self.whitepage = whitepage
        
    def process_whitepage(self, wp_path, request=None):
        if self.tskernel.whitepage==None:
            return (501, "Not Implemented", 'text/plain')
        
        if wp_path.startswith('clues'):
            # clue_path = wp_path[len('clues/'):] #to offer individual access to the clues?
            # Not the best API in the world, but this can be changed in advance
            
            method = request.get_method()
            if method=='GET':
                return (200, """TODO JSON""", 'application/json')
            elif method=='POST':
                clues_json = request.get_data()
                # TODO do something with it
                return (200, """The clue was successfully updated""", 'text/html')


class CustomSimulationHandler(object):
    
    def __init__(self, tskernel):
        self.tskernel = tskernel
    
    def _handleRequest(self, request):
        path = request.get_full_url()
        if path.startswith('/spaces'):
            spaces_path = path[len('/spaces/'):]
            spaces_handler = SpacesHandler(self.tskernel.dataaccess.stores)
            try:
                return spaces_handler.process_spaces(spaces_path, request)
            except Exception, e:
                traceback.print_exc()
                return (500, "Error: %s" % e, 'text/html')
        elif path.startswith('/prefixes'):
            print "prefixes..."
        elif path.startswith('/whitepage'):
            if hasattr(self.tskernel, 'whitepage'):
                whitepage_path = path[len('/whitepage/'):]
                whitepage_handler = WhitepageHandler(self.tskernel.dataaccess.stores)
                return whitepage_handler.process_whitepage(whitepage_path)
            
        return (404, "Not found", 'text/plain')
    
    def _not_handle(self):
        return (503, "Service Unavailable: server overload.", 'text/plain')
    
    def handle(self, request, overload=False):
        status, response, content_type = self._not_handle() if overload else self._handleRequest(request)
        return HttpResponse(request.getid(), response, status=status, headers="Content-Type: %s;"%content_type)
        #self.send_response(code)
        #self.send_header("Content-type", content_type)
        #self.send_header("Content-length", str(len(response)))
        #self.end_headers()
        #self.wfile.write(response)
        #self.wfile.flush()
        #try:
        #    self.connection.shutdown(1)
        #except:
        #    pass