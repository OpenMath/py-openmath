""" Mapping of native Python types to OpenMath """

import six
from . import openmath as om

def to_python(omobj):
    """ Convert OpenMath object to Python """
    if isinstance(omobj, om.OMInteger):
        return omobj.integer
    elif isinstance(omobj, om.OMFloat):
        return omobj.double
    elif isinstance(omobj, om.OMString):
        return omobj.string
    elif isinstance(omobj, om.OMBytes):
        return omobj.bytes
    elif isinstance(omobj, om.OMSymbol):
        if omobj.name == 'infinity':
            return float('inf')
        elif omobj.name == 'true':
            return True
        elif omobj.name == 'false':
            return False
        elif omobj.name == 'emptyset':
            return set()
    elif isinstance(omobj, om.OMApplication) and isinstance(omobj.elem, om.OMSymbol):
        if omobj.elem.name == 'complex_cartesian':
            return complex(omobj.arguments[0].double, omobj.arguments[1].double)
        elif omobj.elem.name == 'list':
            return [to_python(x) for x in omobj.arguments]
        elif omobj.elem.name == 'set':
            return set(to_python(x) for x in omobj.arguments)

    raise ValueError('Cannot convert %s to Python.' % str(omobj))
    
def to_openmath(obj):
    """ Convert Python object to OpenMath """
    if isinstance(obj, bool):
        return om.OMSymbol(str(obj).lower(), cd='logic1')
    elif isinstance(obj, six.integer_types):
        return om.OMInteger(obj)
    elif isinstance(obj, float):
        if obj == float('inf'):
            return om.OMSymbol('infinity', cd='nums1')
        else:
            return om.OMFloat(obj)
    elif isinstance(obj, complex):
        return om.OMApplication(om.OMSymbol('complex_cartesian', cd='complex1'),
                              map(to_openmath, [obj.real, obj.imag]))
    elif isinstance(obj, str):
        return om.OMString(obj)
    elif isinstance(obj, bytes):
        return om.OMBytes(obj)
    elif isinstance(obj, list):
        return om.OMApplication(om.OMSymbol('list', cd='list1'), map(to_openmath, obj))
    elif isinstance(obj, set):
        if obj:
            return om.OMApplication(om.OMSymbol('set', cd='set1'), map(to_openmath, obj))
        else:
            return om.OMSymbol('emptyset', cd='set1')

    raise ValueError('Cannot convert %s to OpenMath.' % str(obj))
