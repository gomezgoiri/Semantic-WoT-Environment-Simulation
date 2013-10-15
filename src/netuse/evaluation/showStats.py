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

from netuse.database.results import HTTPTrace

if __name__ == '__main__':
    for trace in HTTPTrace.objects.order_by('-timestamp'): #(status=200):
        print trace.client, trace.server