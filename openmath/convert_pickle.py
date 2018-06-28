# coding: utf-8
"""
A generic OpenMath exporter for Python based on the pickle protocol

EXAMPLES::

    sage: from openmath.convert_pickle import to_python, to_openmath, test_openmath

Constants::

    sage: to_openmath(False)
    OMSymbol(name='false', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')

``test_openmath`` checks that serializing to openmath and back
rebuilds the same object up to equality::

    sage: test_openmath(False)

    sage: to_openmath(True)
    OMSymbol(name='true', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')
    sage: test_openmath(True)

    sage: to_openmath(None)
    OMSymbol(name='None', cd='__builtin__', id=None, cdbase='http://python.org')
    sage: test_openmath(None)

Strings::

    sage: to_openmath('coucou')
    OMBytes(bytes='coucou', id=None)
    sage: to_python(_)
    'coucou'
    sage: to_openmath(u'coucou')          # todo: not implemented
    OMString(string='coucou', id=None)
    sage: to_python(_)   # todo: not implemented
    'coucou'

Integers::

    sage: to_openmath(3r)
    OMInteger(integer=3, id=None)
    sage: to_python(_)
    3
    sage: test_openmath(3r)

Sage integers::

    sage: to_openmath(3)
    OMApplication(elem=OMSymbol(name='make_integer', cd='sage.rings.integer', id=None, cdbase='http://python.org'),
                  arguments=[OMBytes(bytes='3', id=None)], id=None, cdbase=None)
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

    sage: l = [3r, 1r, 2r]
    sage: to_openmath(l)
    OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
             arguments=[OMInteger(integer=3, id=None),
                        OMInteger(integer=1, id=None),
                        OMInteger(integer=2, id=None)],
             id=None, cdbase=None)

Sets of integers::

    sage: s = {1r}
    sage: to_openmath(s)
    OMApplication(elem=OMSymbol(name='set', cd='__builtin__', id=None, cdbase='http://python.org'),
             arguments=[OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                                 arguments=[OMInteger(integer=1, id=None)],
                                 id=None, cdbase=None)],
             id=None, cdbase=None)
    sage: test_openmath(s)

Lists of sets of Sage integers::

    sage: test_openmath([{1,3}, {2}])

Dictionaries::

    sage: test_openmath({})
    sage: test_openmath({1:3})

Class instances::

    sage: class A(object):
    ....:     def __eq__(self, other):
    ....:         return type(self) is type(other) and self.__dict__ == other.__dict__
    sage: import __main__; __main__.A = A     # Usual trick
    sage: a = A()
    sage: test_openmath(a)
    sage: a.foo = 1
    sage: a.bar = 4
    sage: test_openmath(a)

Functions::

        sage: from openmath import openmath as om
        sage: f = om.OMSymbol(cdbase="http://python.org", cd='math', name='sin')
        sage: o = om.OMApplication(f, [om.OMFloat(3.14)])
        sage: to_python(o)
        0.0015926529164868282

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
from pickle import Pickler, Unpickler, _Stop #, _Unframer, dumps, bytes_types,
import io
import pickle
import importlib
import zlib
from openmath import openmath as om
from six.moves import cStringIO as StringIO
import openmath.convert
from pickle import dumps

def load_python_global(module, name):
    """
    Evaluate an OpenMath symbol describing a global Python object

    EXAMPLES::

        sage: from openmath.convert_pickle import load_python_global, to_python
        sage: load_python_global('math', 'sin')
        <built-in function sin>

        sage: from openmath import openmath as om
        sage: o = om.OMSymbol(cdbase="http://python.org", cd='math', name='sin')
        sage: to_python(o)
        <built-in function sin>
    """
    module = importlib.import_module(module)
    return getattr(module, name)

class PickleConverter:
    def __init__(self):
        self._cdbase="http://python.org"
        self._basic_converter = openmath.convert.BasicPythonConverter()
        self._basic_converter.register_to_python_cdbase(base=self._cdbase, py=load_python_global)

    def to_openmath(self, o=None, sobj=None):
        assert o is None or sobj is None
        if sobj is None:
            sobj = dumps(o)
        str = zlib.decompress(sobj)
        file = StringIO(str)
        # file = io.BytesIO(str) # Python3
        return OMUnpickler(file, self).load()

    def to_python(self, obj):
        return self._basic_converter.to_python(obj)

    ##############################################################################
    # Some new OpenMath constructs
    # Those are mostly lazy versions of unpickling operations (TODO: update this comment)
    ##############################################################################

    def OMSymbol(self, module, name):
        r"""
        Return an OM object for :obj:`None`

        EXAMPLES::

            sage: from openmath.convert_pickle import PickleConverter
            sage: converter = PickleConverter()
            sage: o = converter.OMSymbol(module="foo.bar", name="baz"); o
            OMSymbol(name='baz', cd='foo.bar', id=None, cdbase='http://python.org')
        """
        return om.OMSymbol(cdbase=self._cdbase, cd=module, name=name)

    def OMNone(self):
        r"""
        Return an OM object for :obj:`None`

        EXAMPLES::

            sage: from openmath.convert_pickle import PickleConverter
            sage: converter = PickleConverter()
            sage: o = converter.OMNone(); o
            OMSymbol(name='None', cd='__builtin__', id=None, cdbase='http://python.org')
            sage: converter.to_python(o)
        """
        return self.OMSymbol('__builtin__', name='None')

    def OMList(self, l):
        """
        Convert a list of OM objects into an OM object

        EXAMPLES::

            sage: from openmath import openmath as om
            sage: from openmath.convert_pickle import PickleConverter
            sage: converter = PickleConverter()
            sage: o = converter.OMList([om.OMInteger(2), om.OMInteger(2)]); o
            OMApplication(elem=OMSymbol(name='list', cd='list1', id=None, cdbase='http://www.openmath.org/cd'),
                     arguments=[OMInteger(integer=2, id=None),
                                OMInteger(integer=2, id=None)],
                     id=None, cdbase=None)
            sage: converter.to_python(o)
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

            sage: from openmath import openmath as om
            sage: from openmath.convert_pickle import PickleConverter
            sage: converter = PickleConverter()
            sage: o = converter.OMTuple([om.OMInteger(2), om.OMInteger(3)]); o
            OMApplication(elem=OMSymbol(name='tuple_from_sequence', cd='openmath.convert_pickle', id=None, cdbase='http://python.org'),
              arguments=[OMInteger(integer=2, id=None),
                         OMInteger(integer=3, id=None)],
              id=None, cdbase=None)
            sage: converter.to_python(o)
            (2, 3)
        """
        return om.OMApplication(elem=self.OMSymbol(module='openmath.convert_pickle', name='tuple_from_sequence'),
                                arguments=l)

    def OMDict(self, d):
        """
        Convert a dictionary (or list of items thereof) of OM objects into an OM object

        EXAMPLES::

            sage: from openmath import openmath as om
            sage: from openmath.convert_pickle import PickleConverter
            sage: converter = PickleConverter()
            sage: a = om.OMInteger(1)
            sage: b = om.OMInteger(3)
            sage: o = converter.OMDict([(a,b), (b,b)]); o
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
            sage: converter.to_python(o)
            {1: 3, 3: 3}
        """
        if isinstance(d, dict):
            d = d.items()
        OMList=self.OMList
        return om.OMApplication(elem=self.OMSymbol(module='__builtin__',  name='dict'),
                                arguments=[OMList(OMList(item) for item in d)])


##############################################################################
# Shorthands
##############################################################################

pickle_converter=PickleConverter()
to_openmath = pickle_converter.to_openmath
to_python = pickle_converter.to_python



def OMloads(str):
    str = zlib.decompress(str)
    file = StringIO(str)
    # file = io.BytesIO(str) # Python3
    return OMUnpickler(file).load()

def mydump(obj):
    file = io.StringIO()
    MyPickler(file, protocol=0).dump(obj)
    return file.getvalue()
class MyPickler(Pickler):
    pass


def tuple_from_sequence(*args):
    """
    Construct a tuple from a sequence (not list!) of objects

    EXAMPLES::

        sage: from openmath.convert_pickle import tuple_from_sequence
        sage: tuple_from_sequence(1, 2, 3)
        (1, 2, 3)
        sage: tuple([1, 2, 3])
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

        sage: from openmath.convert_pickle import cls_build
        sage: class A(object): pass
        sage: inst = A.__new__(A)
        sage: state = {"foo": 1, "bar": 4}
        sage: inst2 = cls_build(inst,state)
        sage: inst is inst2
        True
        sage: inst.foo
        1
        sage: inst.bar
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
                for k, v in state.iteritems():
                    d[intern(k)] = v
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

def test_openmath(l):
    o = to_openmath(l)
    l2 = to_python(o)
    assert l == l2
    assert type(l) is type(l2)

class OMUnpickler(Unpickler):
    """
    An unpickler that constructs an OpenMath object whose later
    conversion to evaluation will produce the desired Pytho object.

    This can be seen as a lazy unpickler that produces an OpenMath
    object as intermediate step.
    """
    def __init__(self, file, converter):
        Unpickler.__init__(self, file)
        self._converter = converter

    # Only needed for print-debug purposes
    def load(self):
        """Read a pickled object representation from the open file.

        Return the reconstituted object hierarchy specified in the file.
        """
        self.mark = object() # any new unique object
        self.stack = []
        self.append = self.stack.append
        read = self.read
        dispatch = self.dispatch
        try:
            while 1:
                key = read(1)
                #print(dispatch[key[0]].__name__, self.stack)
                dispatch[key](self)
        except _Stop as stopinst:
            return stopinst.value

    dispatch = { key: Unpickler.dispatch[key]
                 for key in [pickle.PROTO,
                             pickle.STOP,
                             pickle.BINPUT, # ?
                             pickle.BINGET, # ?
                             pickle.MARK,   # ?
                             pickle.TUPLE1, # are those used to produced actual tuples, or only intermediate results?
                             pickle.TUPLE2,
                             pickle.TUPLE3,
                             pickle.EMPTY_TUPLE,
                             pickle.EMPTY_DICT,
                             pickle.NONE,
                             pickle.TUPLE,
                             pickle.SETITEM,
                             pickle.SETITEMS,
                             pickle.NEWFALSE,
                             pickle.NEWTRUE,
                             pickle.INT[0],
                             pickle.BININT1[0],
                             pickle.STRING[0],
                             pickle.SHORT_BINSTRING,
                             pickle.EMPTY_LIST[0],
                             pickle.APPEND[0],
                             pickle.APPENDS[0],
                            ]
               }# copy.copy(Unpickler.dispatch)

    # Finalization
    def load_stop(self):
        value = self.stack.pop()
        value = self.finalize(value)
        raise _Stop(value)
    dispatch[pickle.STOP] = load_stop

    def finalize(self, value):
        converter = self._converter
        if isinstance(value, openmath.openmath.OMApplication):
            for i in range(len(value.arguments)):
                value.arguments[i] = self.finalize(value.arguments[i])
        if isinstance(value, openmath.openmath.OMAny):
            return value
        elif isinstance(value, list):
            return converter.OMList([self.finalize(arg) for arg in value])
        elif isinstance(value, tuple):
            return converter.OMTuple([self.finalize(arg) for arg in value])
        elif isinstance(value, dict):
            return converter.OMDict([(self.finalize(key), self.finalize(v))
                            for key, v in value.items()])
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
