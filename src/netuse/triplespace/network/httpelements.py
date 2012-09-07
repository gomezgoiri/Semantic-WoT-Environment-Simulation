'''
Created on Nov 20, 2011

@author: tulvur
'''
from urllib2 import Request

# http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html
# http://docs.python.org/library/urllib2.html#urllib2.Request
class HttpRequest(Request):
    # Request additional params: reqId, url, data=None, headers={}
    def __init__(self, reqId, url, data=None, headers={}):
        Request.__init__(self, url, data=data, headers=headers)
        self.__reqId = reqId;
        
    def getid(self):
        return self.__reqId
    
# http://love-python.blogspot.com/2008/07/http-response-header-information-in.html
# http://docs.python.org/library/mimetools.html#mimetools.Message
# http://docs.python.org/release/3.0.1/library/http.client.html
class HttpResponse(object):
    """ Inspired in http.client.HTTPResponse objects, which cannot be instantiated """
    def __init__(self, reqId, data, headers=None, status=200, reason="OK", version=11):
        self.__reqId = reqId
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
        
    def getstatus(self):
        """Status code returned by server."""
        return self.__status

    def getreason(self):
        """Reason phrase returned by server."""
        return self.__reason