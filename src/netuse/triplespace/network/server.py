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

import json
import urllib
import traceback
from netuse.triplespace.network.url_utils import URLUtils 
from netuse.triplespace.network.httpelements import HttpResponse

class SpacesHandler(object):
    def __init__(self, stores):
        self.stores = stores

    def process_spaces(self, spaces_path, request=None):
        # Simple list of spaces:
        if spaces_path == '':
            return (200, """Space list (not implemented)""", CustomSimulationHandler.CONTENT_TYPES['html'])

        pos = spaces_path.find('/') 
        if pos >= 0:
            quoted_space = spaces_path[:pos]
        else:
            quoted_space = spaces_path

        space = urllib.unquote(quoted_space)
        if not space in self.stores:
            return (404, """Space not found""", CustomSimulationHandler.CONTENT_TYPES['html'])

        space_operation = spaces_path[len(quoted_space) + 1:] # + 1 for the last '/'
        if space_operation == '':
            return (200, """Operations with space (not implemented)""", CustomSimulationHandler.CONTENT_TYPES['html'])

        store = self.stores[space]

        return self.process_space_operation(store, space_operation, request)

    def process_space_operation(self, store, operation, request):
        if operation.startswith('graphs'):
            graph_operation = operation[len('graphs/'):]
            return self.process_graph_operation(store, graph_operation, request)
        if operation.startswith('query'):
            graph_operation = operation[len('query/'):]
            return self.process_query_operation(store, graph_operation)
        
        return (404, """Method not found""", CustomSimulationHandler.CONTENT_TYPES['html'])
    
    def process_graph_operation(self, store, graph_operation, request):
        if graph_operation == '':
            method = request.get_method()
            if method=='GET':
                return (200, """Graph list (not implemented)""", CustomSimulationHandler.CONTENT_TYPES['html'])
            elif method=='POST':
                actual_graph = request.get_data() # Graph().parse(StringIO.StringIO(request.get_data()), format='n3')
                store.write(actual_graph)
                return (200, """The graph was successfully written""", CustomSimulationHandler.CONTENT_TYPES['html'])
            # cannot be another method, urllib2 does not use them
        
        if graph_operation.find('/') >= 0:
            quoted_graph_uri = graph_operation[:graph_operation.find('/')]
        else:
            quoted_graph_uri = graph_operation

        # Retrieve the graph
        if quoted_graph_uri == 'wildcards':
            wildcard = URLUtils.parse_wildcard_url( graph_operation )
            graph = store.read_wildcard(*wildcard)
        else: # We have an URI
            graph_uri = urllib.unquote(quoted_graph_uri)
            graph = store.read_uri(graph_uri)

        return self.process_graph(graph)
    
    def process_query_operation(self, store, graph_operation):
        if graph_operation == '':
            return (200, """Graph list (not implemented)""", CustomSimulationHandler.CONTENT_TYPES['html'])
        
        if graph_operation.find('/') >= 0:
            quoted_graph_uri = graph_operation[:graph_operation.find('/')]
        else:
            quoted_graph_uri = graph_operation
        
        # Retrieve the graph
        if quoted_graph_uri == 'wildcards':
            wildcard = URLUtils.parse_wildcard_url( graph_operation )
            graph = store.query_wildcard(*wildcard)
            # Except 'caching' strategy the rest don't use the results
            # If we know for sure that we won't simulate 'caching',
            # we can comment the previous sentence and uncomment the following one.
            # Doing so, we may save time by not processing queries.
            #   ( WARNING: not tested how much time or even if it is relevant )
            # graph = None
            return self.process_graph(graph)
        
        return (404, """Method not found""", CustomSimulationHandler.CONTENT_TYPES['html'])

    def process_graph(self, graph):
        if graph is None:
            return (404, """Graph not found""", CustomSimulationHandler.CONTENT_TYPES['html'])
        
        ntriples = graph.serialize(format='n3') # or nt, n3, owl...

        return (200, ntriples, 'text/n3') # text/n-triples, text/n3


class WhitepageHandler(object):
    def __init__(self, tskernel):
        self.tskernel = tskernel
    
    # Not the best API in the world, but this can be changed in advance
    def process_whitepage(self, wp_path, request=None):
        if wp_path.startswith('choose'):
            method = request.get_method()
            if method=='POST':
                # set as whitepage
                data = request.get_data()
                self.tskernel.be_whitepage( None if data=='' else data )
                return (200, """TODO JSON""", CustomSimulationHandler.CONTENT_TYPES['json'])
            
        elif wp_path.startswith('clues'):
            
            if self.tskernel.whitepage==None:
                return (501, "Not Implemented", CustomSimulationHandler.CONTENT_TYPES['plain'])
            
            clues_path = wp_path[len('clues/'):]  #to offer individual access to the clues?
            method = request.get_method()
            
            if len(clues_path)==0:
                if method=='GET':
                    aggregated_clues = self.tskernel.whitepage.get_aggregated_clues_json()
                    return (200, aggregated_clues, CustomSimulationHandler.CONTENT_TYPES['json']) if aggregated_clues!=None else (404, "No clues in this node.", '')
                else:
                    return (405, "Method not allowed", CustomSimulationHandler.CONTENT_TYPES['plain'])
            else: #to offer individual access to the clues, to allow their update or creation
                if method=='POST':
                    node_id = clues_path[:-1] if clues_path.endswith('/') else clues_path
                    self.tskernel.whitepage.add_clue(node_id, request.get_data())
                    json_data = self.tskernel.whitepage.clues.version.to_json()
                    return (200, json_data, CustomSimulationHandler.CONTENT_TYPES['html'])
                else:
                    if clues_path.startswith('query/wildcards/'):
                        wildcard_str = clues_path[len('query/'):]
                        wildcard = URLUtils.parse_wildcard_url(wildcard_str)
                        candidates = list(self.tskernel.whitepage.get_query_candidates(wildcard)) # to convert from set to list
                        return (200, json.dumps(candidates), CustomSimulationHandler.CONTENT_TYPES['json'])
                    else: # FUTURE access to individual clues
                        return (405, "Method not allowed", CustomSimulationHandler.CONTENT_TYPES['plain'])
            
        return (404, """Not found.""", CustomSimulationHandler.CONTENT_TYPES['html'])


class CustomSimulationHandler(object):
    
    CONTENT_TYPES = {'html': 'text/html',
                     'json': 'application/json',
                     'plain': 'text/plain'
                     }
    
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
                return (500, "Error: %s" % e, CustomSimulationHandler.CONTENT_TYPES['html'])
        elif path.startswith('/prefixes'):
            print "prefixes..."
        elif path.startswith('/whitepage'):
            if hasattr(self.tskernel, 'whitepage'):
                whitepage_path = path[len('/whitepage/'):]
                whitepage_handler = WhitepageHandler(self.tskernel)
                return whitepage_handler.process_whitepage(whitepage_path, request)
            
        return (404, "Not found", CustomSimulationHandler.CONTENT_TYPES['plain'])
    
    def _not_handle(self):
        return (503, "Service Unavailable: server overload.", CustomSimulationHandler.CONTENT_TYPES['plain'])
    
    def handle(self, request, overload=False):
        status, response, content_type = self._not_handle() if overload else self._handleRequest(request)
        return HttpResponse(request.getid(), response, url=request.get_full_url(), status=status, headers="Content-Type: %s;"%content_type)
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