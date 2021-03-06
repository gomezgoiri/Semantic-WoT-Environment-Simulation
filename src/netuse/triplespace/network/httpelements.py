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

from urllib2 import Request

# http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html
# http://docs.python.org/library/urllib2.html#urllib2.Request
class HttpRequest(Request):
    # Request additional params: reqId, url, data=None, headers={}
    def __init__(self, reqId, url, data=None, headers={}):
        Request.__init__(self, url, data=data, headers=headers) # old-style class
        self.__reqId = reqId;
        
    def getid(self):
        return self.__reqId
    
# http://love-python.blogspot.com/2008/07/http-response-header-information-in.html
# http://docs.python.org/library/mimetools.html#mimetools.Message
# http://docs.python.org/release/3.0.1/library/http.client.html
class HttpResponse(object):
    """ Inspired in http.client.HTTPResponse objects, which cannot be instantiated """
    def __init__(self, reqId, data, headers=None, status=200, url="",reason="OK", version=11):
        self.__reqId = reqId
        self.__url = url
        self.__status = status
        self.__reason = reason
        self.__headers = headers
        self.__data = data
        
    def getid(self):
        return self.__reqId
    
    def getheader(self, name, default=None):
        """Get the contents of the header name, or default if there is no matching header."""
        if not self.__headers.has_hey(name):
            return default
        else: self.__headers[name]
        
    def getheaders(self):
        """Return a list of (header, value) tuples."""
        return self.__headers
    
    def get_data(self):
        return self.__data
    
    def __str__(self):
        return str(self.getmsg())
    
    def __repr__(self):
        return self.__str__()
        
    def getversion(self):
        """HTTP protocol version used by server. 10 for HTTP/1.0, 11 for HTTP/1.1."""
        return self.__version
    
    def geturl(self):
        """Added to ease the trace."""
        return self.__url    
    
    def getstatus(self):
        """Status code returned by server."""
        return self.__status

    def getreason(self):
        """Reason phrase returned by server."""
        return self.__reason