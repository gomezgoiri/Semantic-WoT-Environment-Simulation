'''
Created on Sep 26, 2012

@author: nctrun

http://code.google.com/p/weblabdeusto/source/browse/server/src/voodoo/MemoryIntrospector.py?r=1b1608dfc72a55d4e4d228673e72b35e911b16e2


Uso:
    introspect()
    raw_input("Before (press enter)")

Y mientras esta parado, miras el dump:
    cat introspection.dump
    Ahi tendras pistas del uso de objetos: ordenados de mayor a menor frecuencia, cuantos son, y con porcentaje.
    

'''

def _dict2list(names, total):
    ordered = [ (obj_name, names[obj_name], 100.0 * names[obj_name] / total) for obj_name in names ]
    ordered.sort(lambda (name1, number1, percent1), (name2, number2, percent2): cmp(number2, number1))
    return ordered

def introspect():
    import gc
    objects = gc.get_objects()
    names = {}
    further_information = {
        '__builtin__.dict' : {},
        '__builtin__.builtin_function_or_method' : {},
    }

    for obj in objects:
        if hasattr(obj, '__class__'):
            obj_name = obj.__class__.__module__ + '.' + obj.__class__.__name__
        else:
            obj_name = '__memory_introspector_other_objs__'

        if obj_name == '__builtin__.dict':
            dict_info = str(obj.keys()[:10])
            further_information[obj_name][dict_info] = further_information[obj_name].get(dict_info, 0) + 1
        elif obj_name == '__builtin__.builtin_function_or_method':
            dict_info = str(obj)[:str(obj).find(" at ")]
            further_information[obj_name][dict_info] = further_information[obj_name].get(dict_info, 0) + 1

        names[obj_name] = names.get(obj_name, 0) + 1

    ordered = _dict2list(names, len(objects))
    open('/tmp/introspection.dump','w').write(str(ordered))
    ordered = _dict2list(further_information['__builtin__.dict'], len(objects))
    open('/tmp/further_introspection_dict.dump','w').write(str(ordered))
    ordered = _dict2list(further_information['__builtin__.builtin_function_or_method'], len(objects))
    open('/tmp/further_introspection_builtin.dump','w').write(str(ordered))