'''
Created on Jan 13, 2013

@author: tulvur
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
    
    def __init__(self, queries, known_answers=[], ttype="QM"):
        if ttype is not "QM" and ttype is not "QU":
            raise Exception("The question type should be rather QM (multicast) or QU (unicast).")
        self.question_type = ttype
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