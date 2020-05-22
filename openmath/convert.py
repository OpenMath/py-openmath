"""
Conversions between Python and OpenMath objects

This module implements conversions from Python objects to OpenMath and
back. All state is encapsulated in instances `c` of the class ``Converter``.
The two main methods are ``to_python()`` and ``to_openmath()``,
which do the conversion as the name suggests, or raise a ``ValueError``
if no conversion is known.

The class ``Converter`` implements no conversion by default. The class
``BasicPythonConverter`` implements conversions in both directions for
basic Python types. For convenience, a default instance
``DefaultConverter`` of the latter is provided.

Examples::

    sage: from openmath.convert import to_openmath, to_python, DefaultConverter

    >>> o = DefaultConverter.to_openmath(1); o
    OMInteger(integer=1, id=None)
    >>> DefaultConverter.to_python(o)
    1

For backward compatibility, one may use the following shorthands::

    >>> o = to_openmath(1); o
    OMInteger(integer=1, id=None)
    >>> to_python(o)
    1

The ``Converter`` class contains a mechanism for registering
additional conversions.

Python to OpenMath conversions
------------------------------

The method ``c.register_to_openmath(py_class, conv)`` registers a
conversion to OpenMath for all instances `x` of the class
``py_class``. If ``py_class`` is ``None``, the registration is for all
Python objects.

If ``conv`` is an OpenMath object, the result of the conversion is
that object. If ``conv`` is a callable, is it called as ``conv(x)``.
It must either return the result of the conversion as an OpenMath
object, or raise an exception. The special exception
``CannotConvertError`` can be used to signify that ``conv`` does not
know how to convert the current object, and that ``to_openmath`` shall
continue with the other converters. Any other exception stops
conversion immediately. Converters registered this way are called in
order from the most recent to the oldest.

Furthermore, any object ``x`` that defines an ``__openmath__``
method will be converted to ``x.__openmath__(converter)``. Inside
this method,``converter`` should be used for recursive conversions.

OpenMath to Python conversion
------------------------------

Four methods are provided for registering additional conversions of OM
objects to Python:

- ``c.register_to_python_class(cls, f)`` registers a conversion from
  any OpenMath object in the class ``cls`` (which should be a subclass
  of ``openmath.OMAny``). The result of the conversion is ``f(x)``.

- ``register_to_python_name(cdbase, cd, name, py)`` registers a
  conversion for the symbol with that name, content dictionary and cd
  base. The result of the conversion is the Python object ``py``;

- ``register_to_python_cd(cdbase, cd, py)`` registers a conversion for
  any symbol ``x`` with that content dictionary and cd base. The
  result of the conversion is ``py(x.name)``;

- ``register_to_python_cdbase(cdbase, py)`` registers a conversion for
  any symbol ``x`` with that cd base. The result of the conversion is
  ``py(x.cd, x.name)``.

"""

import six
from inspect import isclass
from . import openmath as om

class Converter(object):
    """
    A class implementing conversions between native Python and OpenMath objects
    """

    def __init__(self):
        # A list of converters from Python types to OM
        self._conv_to_om = []

        # a dictionary mapping OM classes to converters
        self._omclass_to_py = {}

        # a dictionary to convert OMS elements to Python objects:
        # _oms_to_py((cdbase,cd,name)) = lambda : ...
        # _oms_to_py((cdbase,cd,None)) = lambda name: ...
        # _oms_to_py((cdbase,None,None)) = lambda cd,name: ...
        # _oms_to_py((None,None,None)) = lambda cdbase,cd,name: ...
        self._oms_to_py = {}

    # use this to convert literals or to override the conversion implemented in _oms_to_py
    # any obj of class cls is converted to conv(obj)
    def register_to_python_class(self, cls, conv):
        self._omclass_to_py[cls] = conv

    # registration functions for symbols
    def register_to_python_name(self, base, cd, name, py):
        self._register_to_python(base,cd,name,lambda:py)
    def register_to_python_cd(self, base, cd, py):
        self._register_to_python(base,cd,None,py)
    def register_to_python_cdbase(self, base, py):
        self._register_to_python(base,None,None,py)
    # unifies the above
    def _register_to_python(self, base, cd, name, py):
        self._oms_to_py[(base,cd,name)] = py

    # lookup in _oms_to_py, trying from most to least specific entry
    def _lookup_to_python(self, cdbase, cd, name):
        r = self._oms_to_py.get((cdbase, cd, name))
        if r is not None:
            return r()
        r = self._oms_to_py.get((cdbase, cd, None))
        if r is not None:
            return r(name)
        r = self._oms_to_py.get((cdbase, None, None))
        if r is not None:
            return r(cd,name)
        r = self._oms_to_py.get((None, None, None))
        if r is not None:
            return r(cdbase,cd,name)
        raise ValueError("no entry found for " + cdbase + "?" + cd + "?" + name)


    def to_python(self, omobj):
        """ Convert OpenMath object to Python """
        # general overrides
        if omobj.__class__ in self._omclass_to_py:
            return self._omclass_to_py[omobj.__class__](omobj)
        # oms
        elif isinstance(omobj, om.OMSymbol):
            return self._lookup_to_python(omobj.cdbase, omobj.cd, omobj.name)
        # oma
        elif isinstance(omobj, om.OMApplication):
            elem = self.to_python(omobj.elem)
            arguments = [self.to_python(x) for x in omobj.arguments]
            return elem(*arguments)
        raise ValueError('Cannot convert object of class %s to Python.' % omobj.__class__.__name__)

    def to_openmath(self, obj):
        """ Convert Python object to OpenMath """
        for cl, conv in reversed(self._conv_to_om):
            if cl is None or isinstance(obj, cl):
                try:
                    return conv(obj)
                except CannotConvertError:
                    continue

        if hasattr(obj, '__openmath__'):
            return obj.__openmath__()

        raise ValueError('Cannot convert %r to OpenMath.' % obj)

    def register_to_openmath(self, py_class, converter):
        """Register a conversion from Python to OpenMath

        :param py_class: A Python class the conversion is attached to, or None
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

    # deprecated, made private for now
    def _deprecated_register_to_python(self, cd, name, converter=None):
        """Register a conversion from OpenMath to Python

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

    # deprecated, made private for now
    def _deprecated_register(self, py_class, to_om, om_cd, om_name, to_py=None):
        """
        This is a shorthand for:

           ``self.register_to_python(om_cd, om_name, to_py)``
           ``self.register_to_openmath(py_class, to_om)``
        """
        self.register_to_python(om_cd, om_name, to_py)
        self.register_to_openmath(py_class, to_om)


class BasicPythonConverter(Converter):
    """
    adds conversions for basic Python types:
    - bools,
    - ints,
    - floats,
    - complex numbers (recursively),
    - strings,
    - bytes,
    - ranges,
    - lists (recursively),
    - sets (recursively).
    """
    # base for OM standard CDs
    _omBase = 'http://www.openmath.org/cd'

    def __init__(self):
        super(BasicPythonConverter, self).__init__()
        # to Python

        # primitive operators
        r = lambda cd,name,py: self.register_to_python_name(self._omBase, cd, name, py)
        r('nums1', 'infinity', float('inf'))
        r('logic1', 'true', True)
        r('logic1', 'false', False)
        r('set1', 'emptyset', set())
        r('set1', 'set', lambda *args: set(args))
        r('list1', 'list', lambda *args: list(args))
        r('complex1', 'complex_cartesian', complex) # this does not work if the arguments are not numbers
        r('interval1', 'integer_interval', lambda x,y: range(x, y + 1, 1))

        # literals
        s = self.register_to_python_class
        s(om.OMInteger, lambda o: o.integer)
        s(om.OMFloat,   lambda o: o.double)
        s(om.OMString,  lambda o: o.string)
        s(om.OMBytes,   lambda o: o.bytes)

        # to OpenMath
        t = self.register_to_openmath
        def oms(name, cd):
            return om.OMSymbol(name=name, cd=cd, cdbase=self._omBase)

        for int_type in six.integer_types:
            t(int_type, lambda i: om.OMInteger(i))
        for string_type in six.string_types:
            t(string_type, lambda s: om.OMString(s))
        t(bytes, lambda b: om.OMBytes(b))
        # bool should be registered after int: isinstance(True, int) holds!
        t(bool, lambda b: oms(str(b).lower(), 'logic1'))
        def do_float(f):
            if f == float('inf'):
                return oms('infinity', 'nums1')
            else:
                return om.OMFloat(f)
        t(float, do_float)
        t(complex, lambda c: om.OMApplication(oms('complex_cartesian', 'complex1'), map(self.to_openmath, [c.real, c.imag])))
        t(list, lambda l: om.OMApplication(oms('list','list1'), map(self.to_openmath, l)))
        def do_set(s):
            if s:
                return om.OMApplication(oms('set', 'set1'), map(self.to_openmath, s))
            else:
                return oms('emptyset', cd='set1')
        t(set, do_set)
        def do_range(r):
            if r.step != 1:
                raise ValueError('Cannot convert %r to OpenMath: Range must have a step of 1. ' % obj)
            return om.OMApplication(oms('integer_interval', 'interval1'), [om.OMInteger(r.start), om.OMInteger(r.stop - 1)])
        t(range, do_range)



# A default converter instance for convenience
DefaultConverter = BasicPythonConverter()

# Shorthands for backward compatibility (and convenience?)
to_python = DefaultConverter.to_python
to_openmath = DefaultConverter.to_openmath
#register = DefaultConverter.register # not used anymore
register_to_openmath = DefaultConverter.register_to_openmath
register_to_python_class = DefaultConverter.register_to_python_class

class CannotConvertError(RuntimeError):
    """
    Raise this exception if your converter to OpenMath is not able
    to handle the inputs.
    """
    pass
