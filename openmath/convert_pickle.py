# coding: utf-8
"""
A generic OpenMath exporter for Python based on the pickle protocol

Note: the current implementation works only with Python 2, due to
reliance on internals of Python's pickle that have changed in Python 3.

EXAMPLES::

    >>> from openmath.convert_pickle import to_python, to_openmath, test_openmath

Constants::

    >>> to_openmath(False)
    OMSymbol(name='false', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')

``test_openmath`` checks that serializing to openmath and back
rebuilds the same object up to equality::

    >>> test_openmath(False)

    >>> to_openmath(True)
    OMSymbol(name='true', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')
    >>> test_openmath(True)

    >>> to_openmath(None)
    OMSymbol(name='None', cd='__builtin__', id=None, cdbase='http://python.org')
    >>> test_openmath(None)

Strings::

    >>> to_openmath('coucou')
    OMString(string='coucou', id=None)
    >>> to_python(_)
    'coucou'

Unicode strings are not yet supported

    > to_openmath(u'coucou')           # doctest: +SKIP
    OMString(string='coucou', id=None)
    > to_python(_)                     # doctest: +SKIP
    'coucou'

Integers::

    >>> to_openmath(3)
    OMInteger(integer=3, id=None)
    >>> to_python(_)
    3
    >>> test_openmath(3)

Sage integers::

    sage: to_openmath(3)
    OMApplication(elem=OMSymbol(name='make_integer', cd='sage.rings.integer', id=None, cdbase='http://python.org'),
                  arguments=[OMString(string='3', id=None)], id=None, cdbase=None)
    sage: test_openmath(3)

Sage real numbers::

    sage: test_openmath(1.1+1.1)

But not quite yet real literals::

    sage: test_openmath(1.1)
    Traceback (most recent call last):
    ...
    AssertionError
    sage: l = 1.1
    sage: o = to_openmath(1.1)
    sage: l2 = to_python(o); l2
    1.10000000000000
    sage: l2 == l
    True
    sage: type(l2)
    <type 'sage.rings.real_mpfr.RealNumber'>
    sage: type(l)
    <type 'sage.rings.real_mpfr.RealLiteral'>

Lists of integers::

    >>> l = [3, 1, 2]
    >>> to_openmath(l)
    OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
             arguments=[OMInteger(integer=3, id=None),
                        OMInteger(integer=1, id=None),
                        OMInteger(integer=2, id=None)],
             id=None, cdbase=None)

Sets of integers::

    >>> s = {1}
    >>> to_openmath(s)
    OMApplication(elem=OMSymbol(name='set', cd='__builtin__', id=None, cdbase='http://python.org'),
             arguments=[OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                                 arguments=[OMInteger(integer=1, id=None)],
                                 id=None, cdbase=None)],
             id=None, cdbase=None)
    >>> test_openmath(s)

Lists of sets of Sage integers::

    sage: test_openmath([{1,3}, {2}])

Dictionaries::

    >>> test_openmath({})
    >>> test_openmath({1:3})

Class instances::
    >>> import openmath.convert_pickle
    >>> class A(object):
    ...     def __eq__(self, other):
    ...         return type(self) is type(other) and self.__dict__ == other.__dict__
    >>> import __main__; __main__.A = A     # Usual trick
    >>> openmath.convert_pickle.A = A       # Idem
    >>> a = A()
    >>> test_openmath(a)
    >>> a.foo = 1
    >>> a.bar = 4
    >>> test_openmath(a)

Functions::

    >>> from openmath import openmath as om
    >>> f = om.OMSymbol(cdbase="http://python.org", cd='math', name='sin')
    >>> o = om.OMApplication(f, [om.OMFloat(3.14)])
    >>> to_python(o)
    0.0015926529164868282
    >>> import math
    >>> test_openmath(math.sin)

Sage parents::

    sage: test_openmath(Partitions(3))
    sage: test_openmath(QQ)
    sage: test_openmath(RR)
    sage: test_openmath(Algebras(QQ))
    sage: test_openmath(SymmetricFunctions(QQ))
    sage: test_openmath(SymmetricFunctions(QQ).s())
    sage: test_openmath(GF(3))

Sage objects::

    sage: to_openmath(Partition([2,1]))
    OMApplication(...)
    sage: test_openmath(Partition([2,1]))
"""

from __future__ import absolute_import
import importlib

import openmath.convert
from openmath import openmath as om

import zlib

import six
import six.moves

import pickle

##############################################################################
# PickleConverter -- main class
##############################################################################

class PickleConverter:
    def __init__(self):
        self._cdbase="http://python.org"
        self._basic_converter = openmath.convert.BasicPythonConverter()
        self._basic_converter.register_to_python_cdbase(base=self._cdbase, py=load_python_global)

    def to_python(self, obj):
        return self._basic_converter.to_python(obj)

    def to_openmath(self, o=None, sobj=None):
        assert o is None or sobj is None
        if sobj is None:
            sobj = pickle.dumps(o, protocol=2)
        file = six.BytesIO(sobj)
        
        return OMUnpickler(file, self).load()

    ##############################################################################
    # Some new OpenMath constructs
    # Those are mostly lazy versions of unpickling operations (TODO: update this comment)
    ##############################################################################

    def OMSymbol(self, module, name):
        r"""
        Helper function to build an OMS object
        
        EXAMPLES::

            >>> from openmath.convert_pickle import PickleConverter
            >>> converter = PickleConverter()
            >>> o = converter.OMSymbol(module="foo.bar", name="baz"); o
            OMSymbol(name='baz', cd='foo.bar', id=None, cdbase='http://python.org')
        """
        return om.OMSymbol(cdbase=self._cdbase, cd=module, name=name)

    def OMNone(self):
        r"""
        Return an OM object for :obj:`None`

        EXAMPLES::

            >>> from openmath.convert_pickle  import PickleConverter
            >>> converter = PickleConverter()
            >>> o = converter.OMNone(); o
            OMSymbol(name='None', cd='__builtin__', id=None, cdbase='http://python.org')
            >>> converter.to_python(o)
        """
        return self.OMSymbol('__builtin__', name='None')

    def OMList(self, l):
        """
        Convert a list of OM objects into an OM object

        EXAMPLES::

            >>> from openmath import openmath as om
            >>> from openmath.convert_pickle  import PickleConverter
            >>> converter = PickleConverter()
            >>> o = converter.OMList([om.OMInteger(2), om.OMInteger(2)]); o
            OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                     arguments=[OMInteger(integer=2, id=None),
                                OMInteger(integer=2, id=None)],
                     id=None, cdbase=None)
            >>> converter.to_python(o)
            [2, 2]
        """
        # Except for the conversion of operands, this duplicates the default
        # implementation of python's list conversion to openmath in py_openmath
        return om.OMApplication(elem=om.OMSymbol(cdbase=self._basic_converter._omBase, cd='list1', name='list', ),
                                arguments=l)

    def OMTuple(self, l):
        """
        Convert a list of OM objects into an OM object

        EXAMPLES::

            >>> from openmath import openmath as om
            >>> from openmath.convert_pickle  import PickleConverter
            >>> converter = PickleConverter()
            >>> o = converter.OMTuple([om.OMInteger(2), om.OMInteger(3)]); o
            OMApplication(elem=OMSymbol(name='tuple_from_sequence', cd='openmath.convert_pickle', id=None, cdbase='http://python.org'),
              arguments=[OMInteger(integer=2, id=None),
                         OMInteger(integer=3, id=None)],
              id=None, cdbase=None)
            >>> converter.to_python(o)
            (2, 3)
        """
        return om.OMApplication(elem=self.OMSymbol(module='openmath.convert_pickle', name='tuple_from_sequence'),
                                arguments=l)

    def OMDict(self, d):
        """
        Convert a dictionary (or list of items thereof) of OM objects into an OM object

        EXAMPLES::

            >>> from openmath import openmath as om
            >>> from openmath.convert_pickle  import PickleConverter
            >>> converter = PickleConverter()
            >>> a = om.OMInteger(1)
            >>> b = om.OMInteger(3)
            >>> o = converter.OMDict([(a,b), (b,b)]); o
            OMApplication(elem=OMSymbol(name='dict', cd='__builtin__', id=None, cdbase='http://python.org'),
              arguments=[OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                  arguments=[OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                      arguments=[OMInteger(integer=1, id=None), OMInteger(integer=3, id=None)], id=None, cdbase=None),
                    OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                      arguments=[OMInteger(integer=3, id=None),
                                 OMInteger(integer=3, id=None)],
                      id=None, cdbase=None)],
                  id=None, cdbase=None)],
                id=None, cdbase=None)
            >>> converter.to_python(o)
            {1: 3, 3: 3}
        """
        if isinstance(d, dict):
            d = d.items()
        OMList=self.OMList
        return om.OMApplication(elem=self.OMSymbol(module='__builtin__',  name='dict'),
                                arguments=[OMList(OMList(item) for item in d)])

def load_python_global(module, name):
    """
    Evaluate an OpenMath symbol describing a global Python object

    EXAMPLES::

        >>> from openmath.convert_pickle import to_python
        >>> from openmath.convert_pickle  import load_python_global
        >>> load_python_global('math', 'sin')
        <built-in function sin>

        >>> from openmath import openmath as om
        >>> o = om.OMSymbol(cdbase="http://python.org", cd='math', name='sin')
        >>> to_python(o)
        <built-in function sin>
    """

    # The builtin module has been renamed in python3
    if module == '__builtin__' and six.PY3:
        module = 'builtins'
    module = importlib.import_module(module)
    return getattr(module, name)


##############################################################################
# Generic Object Constructors for loading objects
##############################################################################

def tuple_from_sequence(*args):
    """
    Construct a tuple from a sequence (not list!) of objects

    EXAMPLES::

        >>> from openmath.convert_pickle import tuple_from_sequence
        >>> tuple_from_sequence(1, 2, 3)
        (1, 2, 3)
        >>> tuple([1, 2, 3])
        (1, 2, 3)
    """
    return tuple(args)

def cls_new(cls, *args):
    return cls.__new__(cls, *args)

def cls_build(inst, state):
    """
    Apply the setstate protocol to initialize `inst` from `state`.

    INPUT:

    - ``inst`` -- a raw instance of a class
    - ``state`` -- the state to restore; typically a dictionary mapping attribute names to their values

    EXAMPLES::

        >>> from openmath.convert_pickle import cls_build
        >>> class A(object): pass
        >>> inst = A.__new__(A)
        >>> state = {"foo": 1, "bar": 4}
        >>> inst2 = cls_build(inst,state)
        >>> inst is inst2
        True
        >>> inst.foo
        1
        >>> inst.bar
        4
    """
    # Copied from Pickler.load_build
    setstate = getattr(inst, "__setstate__", None)
    if setstate:
        setstate(state)
        return inst
    slotstate = None
    if isinstance(state, tuple) and len(state) == 2:
        state, slotstate = state
    
    if state:
        try:
            d = inst.__dict__
            try:
                for k, v in six.iteritems(state):
                    d[six.moves.intern(k)] = v
            # keys in state don't have to be strings
            # don't blow up, but don't go out of our way
            except TypeError:
                d.update(state)

        except RuntimeError:
            # XXX In restricted execution, the instance's __dict__
            # is not accessible.  Use the old way of unpickling
            # the instance variables.  This is a semantic
            # difference when unpickling in restricted
            # vs. unrestricted modes.
            # Note, however, that cPickle has never tried to do the
            # .update() business, and always uses
            #     PyObject_SetItem(inst.__dict__, key, value) in a
            # loop over state.items().
            for k, v in state.items():
                setattr(inst, k, v)
    if slotstate:
        for k, v in slotstate.items():
            setattr(inst, k, v)
    return inst

##############################################################################
# Unpickler -- turns a pickled object into OpenMath
##############################################################################

# check if we have the dispatch attribute on the Unpickler class
# if not, fall back to the _Unpickler version (python3)
if hasattr(pickle.Unpickler, 'dispatch'):
    _Unpickler = pickle.Unpickler
else:
    _Unpickler = pickle._Unpickler

class OMUnpickler(_Unpickler):
    """
    An unpickler that constructs an OpenMath object whose later
    conversion to evaluation will produce the desired Python object.

    This can be seen as a lazy unpickler that produces an OpenMath
    object as intermediate step.
    """
    def __init__(self, file, converter):
        _Unpickler.__init__(self, file)
        self._converter = converter
    
    # we need to do this twice to enable stuff
    dispatch = dict(_Unpickler.dispatch)
    
    # Finalization
    def load_stop(self):
        value = self.stack.pop()
        value = self.finalize(value)
        raise pickle._Stop(value)
    dispatch[pickle.STOP] = load_stop # Python 2
    dispatch[pickle.STOP[0]] = load_stop # Python 3

    def finalize(self, value):
        converter = self._converter
        if isinstance(value, om.OMApplication):
            for i in range(len(value.arguments)):
                value.arguments[i] = self.finalize(value.arguments[i])
        if isinstance(value, om.OMAny):
            return value
        elif isinstance(value, list):
            return converter.OMList([self.finalize(arg) for arg in value])
        elif isinstance(value, tuple):
            return converter.OMTuple([self.finalize(arg) for arg in value])
        elif isinstance(value, dict):
            return converter.OMDict([(self.finalize(key), self.finalize(v))
                            for key, v in value.items()])
        elif isinstance(value, six.string_types):
            return om.OMString(string=value)
        elif value is None:
            return converter.OMNone()
        else:
            return converter._basic_converter.to_openmath(value)

    def load_global(self):
        module = self.readline()[:-1].decode("utf-8")
        name = self.readline()[:-1].decode("utf-8")
        #func_name = module+"."+name
        # Variant: om.OMSymbol(name='func_name', **cd_of(func_name))
        # where cd_of would return {'cdbase': 'sagemath.org', 'cd': 'sagemath'}
        #self.append(om.OMApplication(om.OMSymbol(name='load_global', cd='python'),
        #                             [om.OMString(func_name)]))
        #def func(*args):
        #    return om.OMApplication(om.OMSymbol(name='apply_function', cd='python'),
        #                            (om.OMString(func_name),)+args)
        #self.append(func)
        OMSymbol = self._converter.OMSymbol
        self.append(OMSymbol(module=module, name=name))
    dispatch[pickle.GLOBAL[0]] = load_global

    def load_reduce(self):
        stack = self.stack
        args = stack.pop()
        func = stack[-1]
        stack[-1] = om.OMApplication(func, args)
    dispatch[pickle.REDUCE[0]] = load_reduce

    def load_newobj(self):
        args = self.stack.pop()
        cls = self.stack.pop()
        OMSymbol = self._converter.OMSymbol
        obj =  om.OMApplication(OMSymbol(module="openmath.convert_pickle", name='cls_new'),
                                (cls,) + args)
        self.append(obj)
    dispatch[pickle.NEWOBJ[0]] = load_newobj

    def load_build(self):
        stack = self.stack
        state = stack.pop()
        inst = stack.pop()
        OMSymbol = self._converter.OMSymbol
        obj =  om.OMApplication(OMSymbol(module="openmath.convert_pickle", name='cls_build'),
                                (inst, state))
        self.append(obj)
    dispatch[pickle.BUILD[0]] = load_build

##############################################################################
# Shorthands
##############################################################################

pickle_converter=PickleConverter()
to_openmath = pickle_converter.to_openmath
to_python = pickle_converter.to_python

def OMloads(str):
    str = zlib.decompress(str)
    file = six.BytesIO(str)
    return OMUnpickler(file).load()

def test_openmath(l):
    """
    Test that we can convert an object to openmath and back

    EXAMPLES::

        >>> from openmath.convert_pickle import test_openmath
        >>> test_openmath([1, 2, 3])
    """
    o = to_openmath(l)
    l2 = to_python(o)
    assert l == l2
    assert type(l) is type(l2)

"""

# In[73]:



# In[74]:



# In[75]:


class A:
    pass
a = A()
a.x=3


# In[76]:


t = OMloads(dumps(a))
print(t)
a2 = to_python(t)
print(a2)


# In[70]:


a2.x



"""
