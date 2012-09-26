'''
Created on Sep 26, 2012

@author: nctrun

Hack para python para sobreescribir una clase hecha por terceros (o por mi) y saber cual es su origen (donde se creo).
'''
import urllib2
import traceback
import StringIO
import gc

# Sobreescribe el metodo init de la clase para meterle un traceo de donde se ha creado
def generate(klass):

        old_init = klass.__init__

        def fake_init(self, *args, **kwargs):
                old_init(self, *args, **kwargs)
                sio = StringIO.StringIO()
                traceback.print_stack(file=sio)
                self._debugging_creation = sio.getvalue()
        klass.__init__ = fake_init

# Clases de ejemplo

# El garbage collector la trataria bien
class Buena(object):
        def __init__(self, ref):
                self.ref = ref

class A(object):    
    def __del__(self):
        print "Me muero: " + self.name

# El garbage collector no sabria como eliminarla de memoria y la dejaria en gc.garbage
class Mala(object):
    def __init__(self, ref):
            self.ref = ref
            self.a = A()
            self.a.mala = self
    
    def __del__(self):
        print "Me muero: " + self.name



# Genero muchos objetos buenos (que dejaran de estar en memoria cuando los recoja el GC)
def f():
        lista = []
        for _ in xrange(1000):
                lista.append(Buena(urllib2.Request('/')))

# Genero muchos objetos malos (que persistiran en memoria por tener referencias cruzadas)
def g():
        lista = []
        for _ in xrange(1000):
                lista.append(Mala(urllib2.Request('')))


if __name__ == '__main__':
    # hack para hacer una clase cualquiera traceable (que tenga el atributo _debugging_creation con la traza
    generate(urllib2.Request)
    
    
    # Llamo a las funciones que generan listas con muchos objetos
    f()
    g()
    
    # Fuerzo que se eliminen objetos en memoria
    gc.collect()
    
    # Asi, si tienes un objeto que se te ha quedado en memoria, puedes conocer su origen con _debugging_creation 
    remaining = [ obj._debugging_creation for obj in gc.get_objects() if isinstance(obj, urllib2.Request) ]
    
    # Ves donde se crearon los objetos que se mantuvieron en memoria
    for i in remaining:
            print i
    
    print gc.garbage