'''
Created on Sep 26, 2012

@author: tulvur

http://docs.python.org/library/profile.html
'''

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