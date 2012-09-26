'''
Created on Sep 26, 2012

@author: tulvur
'''
import gc

class A(object):
    def __init__(self, name):
        self.name = name
        self.a = None
        self.b = None

    def __del__(self):
        print "Me muero: " + self.name

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