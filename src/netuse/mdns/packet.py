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

class DNSPacket(object):
    
    TYPE_QUERY = "query"
    TYPE_RESPONSE = "response"
    
    def __init__(self, ttype, data):
        if ttype != DNSPacket.TYPE_QUERY and ttype != DNSPacket.TYPE_RESPONSE:
            raise Exception("The DNS packet should be a 'query' or a 'response'.")
        self.type = ttype
        self.data = data

class Query(object):
    
    def __init__(self, queries, known_answers=[], to_node=None):
        self.question_type = "QM" if to_node is None else "QU"
        if to_node is not None:
            self.to_node = to_node # is defined on queries willing to receive an unicast response (QU)
        self.known_answers = known_answers # for the known answer suppression, records
        self.queries = queries # SubQuery objects
        # to browse, the name should be _services._dns-sd._udp.local

    def response_is_unique(self):
        if len(self.queries)!=1: return False
        rec_t = self.queries[0].record_type
        return rec_t is "TXT" or rec_t is "SVR" # not the case of the "PTR" record!

        
class SubQuery(object):
    
    def __init__(self, name, record_type):
        self.name = name
        self.record_type = record_type