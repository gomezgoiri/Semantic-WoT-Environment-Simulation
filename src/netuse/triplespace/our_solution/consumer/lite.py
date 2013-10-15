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
from netuse.triplespace.network.url_utils import URLUtils
from netuse.triplespace.our_solution.consumer.consumer import AbstractConsumer, AbstractConnector
from netuse.triplespace.network.client import RequestInstance, RequestManager, RequestObserver


class ConsumerLite(AbstractConsumer):
    def _update_connector(self, wp):
        if wp==self.discovery.me:
            raise Exception("A lite consumer cannot act as a whitepage, check the selection algorithm.")
        else:
            if self.connector is None:
                self.connector = RemoteLiteConnector(self.discovery.me, wp, simulation=self.simulation)
                self.connector.start()
                # when to self.connector.stop() ???
            else:
                # reusing the same connector
                self.connector.change_whitepage( wp )


class RemoteLiteConnector(AbstractConnector, RequestObserver):
    
    def __init__(self, me_as_node, whitepage_node, simulation):
        self.me_as_node = me_as_node
        self.whitepage_node = whitepage_node
        self.simulation = simulation
        self.responses = {}
    
    def _get_candidates_from_wp_request(self, templateURL):
        req = RequestInstance( self.me_as_node,
                               [self.whitepage_node],
                               '/whitepage/clues/query/%s'%(templateURL),
                               sim = self.simulation )
        req.addObserver(self)
        return req
    
    def notifyRequestFinished(self, request_instance):
        for unique_response in request_instance.responses:
            if unique_response.getstatus()==200:
                # get the template URL requested
                pattern = "/whitepage/clues/query/"
                path = unique_response.geturl()
                pos = path.find(pattern) + len(pattern) # it could be len(pattern) since pattern will be always at the beginning
                templateURL = path[pos:]
                
                # parse a list of names (nodes)
                list_candidates = json.loads(unique_response.get_data())
                self.responses[templateURL] = list_candidates
                
                break
            else:
                # TODO
                # What has happened? How to solve it?
                pass
    
    def get_query_candidates(self, template, previously_unsolved=False):
        templateURL = URLUtils.serialize_wildcard_to_URL(template)
        
        if templateURL in self.responses.keys():
            if self.responses[templateURL] is None:
                raise Exception("Wait for the answer.")
            else:
                # take the response
                candidates = self.responses[templateURL]
                del self.responses[templateURL]
                return candidates
        else:
            self.responses[templateURL] = None # create a slot to store the response later and warn that it's being requested until then
            RequestManager.launchNormalRequest(self._get_candidates_from_wp_request(templateURL))
            return None # waiting for it
    
    def change_whitepage(self, whitepage_node):
        # nothing scheduled, so I simply change the WP for the next call to get_query_candidates
        self.whitepage_node = whitepage_node