"""
Mapping of native Python types to OpenMath

This modules implements conversions from Python objects to OpenMath and
back. All state is encapsulated in a class called ``Converter``. For
convenience, a default instance ``DefaultConverter`` is provided.

The two main functions are ``to_python()`` and ``to_openmath()``,
which do the conversion as the name suggests, or raise a ``ValueError``
if no conversion is known.

By default, a Converter class only implements conversions for basic Python
types:

- bools,
- ints,
- floats,
- complex numbers,
- strings,
- bytes,
- lists (recursively),
- sets (recursively).

Furthermore, any object that defines an ``__openmath__(self)`` method
will get that method called by ``to_python``.

Finally, the class contains a mechanism for registering converters.

The function ``register_to_python()`` takes either two or three inputs.
The form ``register_to_python(om_class, conv)`` expects a subclass of
``openmath.OMAny`` as first parameter, and a function as second
parameter. Any object of type ``om_class`` will be passed to ``conv()``,
and the result will be returned.

The form ``register_to_python(cd, name, conv)`` expects two strings for
the arguments ``cd`` and ``name``, and any object for the third
argument. Any object of type ``openmath.OMSymbol``, with content
dictionary equal to ``cd`` and name equal to ``name`` will be converted
using ``conv``. Also, any object of type ``openmath.OMApplication``
whose first child is an ``openmath.OMSymbol`` as above will be converted
using ``conv``. If ``conv`` is a function, it will be called with the
OpenMath object as parameter; otherwise ``conv`` will be returned.

The function ``register_to_openmath(py_class, conv)`` takes two
parameters, the first being None, or a Python class, the second being a
function or an OpenMath object. ``conv`` is used to convert any object
of type ``py_class``, or any object if ``py_class`` is ``None``. If
``conv`` is an OpenMath object, it is returned immediately. If it is a
callable, it is called with the Python object as paramter; in this case,
it must either return an OpenMath object, or raise an exception. The
special exception ``CannotConvertError`` can be used to signify that
``conv`` does not know how to convert the current object, and that
``to_openmath`` shall continue with the other converters. Any other
exception stops conversion immediately.  Converters registered this way
are called in order from the most recent to the oldest.

Finally, the function ``register()`` may be used as a shortcut for the
two previous functions.
"""

import six
from inspect import isclass
from . import openmath as om

class Converter(object):
    """
    A class implementing conversion between native Python and OpenMath objects
    """
    def __init__(self):
        # A list of converters from python types to OM
        self._conv_to_om = []

        # A dictionary to override OM basic tags
        self._conv_to_py = {}
        # A dictionary to convert OM symbols
        self._conv_sym_to_py = {
            ('nums1', 'infinity'):             float('inf'),
            ('logic1', 'true'):                True,
            ('logic1', 'false'):               False,
            ('list1', 'list'):                 lambda obj: [self.to_python(x) for x in obj.arguments],
            ('set1', 'emptyset'):              set(),
            ('set1', 'set'):                   lambda obj: set(self.to_python(x) for x in obj.arguments),
            ('complex1', 'complex_cartesian'): lambda obj: complex(obj.arguments[0].double, obj.arguments[1].double),
        }
    
    def to_python(self, omobj):
        """ Convert OpenMath object to Python """
        if omobj.__class__ in self._conv_to_py:
            return self._conv_to_py[omobj.__class__](omobj)
        elif isinstance(omobj, om.OMInteger):
            return omobj.integer
        elif isinstance(omobj, om.OMFloat):
            return omobj.double
        elif isinstance(omobj, om.OMString):
            return omobj.string
        elif isinstance(omobj, om.OMBytes):
            return omobj.bytes
        elif isinstance(omobj, om.OMSymbol):
            val = self._conv_sym_to_py.get((omobj.cd, omobj.name))
            if val is not None:
                if callable(val):
                    return val(omobj)
                else:
                    return val
        elif isinstance(omobj, om.OMApplication) and isinstance(omobj.elem, om.OMSymbol):
            val = self._conv_sym_to_py.get((omobj.elem.cd, omobj.elem.name))
            if val is not None:
                if callable(val):
                    return val(omobj)
                else:
                    return val

        raise ValueError('Cannot convert object of class %s to Python.' % omobj.__class__.__name__)
    
    def to_openmath(self, obj):
        """ Convert Python object to OpenMath """
        for cl, conv in reversed(self._conv_to_om):
            if cl is None or isinstance(obj, cl):
                try:
                    if callable(conv):
                        return conv(obj)
                    else:
                        return conv
                except CannotConvertError:
                    continue

        if hasattr(obj, '__openmath__'):
            return obj.__openmath__()

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
                                  map(self.to_openmath, [obj.real, obj.imag]))
        elif isinstance(obj, str):
            return om.OMString(obj)
        elif isinstance(obj, bytes):
            return om.OMBytes(obj)
        elif isinstance(obj, list):
            return om.OMApplication(om.OMSymbol('list', cd='list1'), map(self.to_openmath, obj))
        elif isinstance(obj, set):
            if obj:
                return om.OMApplication(om.OMSymbol('set', cd='set1'), map(self.to_openmath, obj))
            else:
                return om.OMSymbol('emptyset', cd='set1')

        raise ValueError('Cannot convert %r to OpenMath.' % obj)

    def register_to_openmath(self, py_class, converter):
        """Register a converter from Python to OpenMath

        :param py_class: A Python class the converter is attached to, or None
        :type py_class: None, type

        :param converter: A conversion function or an OpenMath object
        :type converter: Callable, OMAny

        :rtype: None

        ``converter`` will used to convert any object of type ``py_class``,
        or any object if ``py_class`` is ``None``. If ``converter`` is an
        OpenMath object, it is returned immediately. If it is a callable, it
        is called with the Python object as paramter; in this case, it must
        either return an OpenMath object, or raise an exception.  The
        special exception ``CannotConvertError`` can be used to signify that
        ``converter`` does not know how to convert the current object, and that
        ``to_openmath`` shall continue with the other converters. Any other
        exception stops conversion immediately.

        Converters registered by this function are called in order from the
        most recent to the oldest.
        """
        if py_class is not None and not isclass(py_class):
            raise TypeError('Expected class, found %r' % py_class)
        if not callable(converter) and not isinstance(converter, om.OMAny):
            raise TypeError('Expected callable or openmath.OMAny object, found %r' % converter)
        self._conv_to_om.append((py_class, converter))

    def register_to_python(self, cd, name, converter=None):
        """Register a converter from OpenMath to Python

        This function has two forms. A three-arguments one:

        :param cd: A content dictionary name
        :type cd: str

        :param name: A symbol name
        :type name: str

        :param converter: A conversion function, or a Python object
        :type: Callable, Any

        Any object of type ``openmath.OMSymbol``, with content
        dictionary equal to ``cd`` and name equal to ``name`` will be converted
        using ``converter``. Also, any object of type ``openmath.OMApplication``
        whose first child is an ``openmath.OMSymbol`` as above will be converted
        using ``converter``. If ``converter`` is a callable, it will be called with the
        OpenMath object as parameter; otherwise ``converter`` will be returned.

        In the two-argument form

        :param cd: A subclass of ``OMAny``
        :type cd: type

        :param name: A conversion function
        :type name: Callable

        Any object of type ``cd`` will be passed to ``name()``, and the
        result will be returned. This forms is mainly to override default
        conversions for basic OpenMath tags (OMInteger, OMString, etc.). It
        is discouraged to use it for ``OMSymbol`` and ``OMApplication``.
        """
        if converter is None:
            if isclass(cd) and issubclass(cd, om.OMAny):
                self._conv_to_py[cd] = name
            else:
                raise TypeError('Two-arguments form expects subclass of openmath.OMAny, found %r' % cd)
        else:
            if isinstance(cd, str) and isinstance(name, str):
                self._conv_sym_to_py[(cd, name)] = converter
            else:
                raise TypeError('Three-arguments form expects string, found %r' % cd.__class__)

    def register(self, py_class, to_om, om_cd, om_name, to_py=None):
        """
        Shorthand for

        >>> self.register_to_python(om_cd, om_name, to_py)
        >>> self.register_to_openmath(py_class, to_om)
        """
        self.register_to_python(om_cd, om_name, to_py)
        self.register_to_openmath(py_class, to_om)


# A default converter instance for convenience
DefaultConverter = Converter()

class CannotConvertError(RuntimeError):
    """
    Raise this exception if your converter to OpenMath is not able
    to handle the inputs.
    """
    pass