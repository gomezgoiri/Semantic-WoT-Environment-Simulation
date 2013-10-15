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
 
# See: http://docs.python.org/library/profile.html

import cProfile as profile
import time

def h():
        time.sleep(0.01)

def g():
        for _ in xrange(10):
                h()

def f():
        g()

obj = profile.run("f()", '/tmp/output.txt')
print obj

import pstats
p = pstats.Stats('/tmp/output.txt')
# y con ese objeto "p" ya sacas muchos mas datos de los que te aparecen en el resumen de profile.run

# Con runsnakerun puedes verlo gráficamente, si consigues configurar wxgtk y demás dependencias graficas