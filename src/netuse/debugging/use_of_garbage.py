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
import gc

class A(object):
    def __init__(self, name):
        self.name = name
        self.a = None
        self.b = None

    def __del__(self):
        print "Me muero: " + self.name

if __name__ == '__main__':
    a = A("a")
    b = A("b")
    a.b = b
    b.a = a
    a = None
    b = None
    
    c = A("c")
    
    gc.collect()
    
    # Referencia circular en aquellos que tienen __del__() redefinido hace que no lo elimine por precaucion
    #     (no sabe como eliminarlo, que eliminar antes...)
    # Deja la posible mierda en gc.garbage
    print gc.garbage