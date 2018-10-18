# coding: utf-8
"""
Helpers to use OpenMath as a DSL in Python

EXAMPLES::

We first define:

>>> cd = CDBaseHelper('http://www.openmath.org/cd')

and then be able to use this as follows:

>>> one_plus_one = cd.arith1.plus(1, 1)
>>> print(one_plus_one)
    OMApplication(
      elem=OMSymbol(name='plus', cd='arith1', cdbase='http://www.openmath.org/cd'),
      arguments=[
        OMInteger(integer=1),
        OMInteger(integer=1)])

The use for this becomes apparent for larger terms, such as the quadratic formula
example as found on Wikipedia:

>>> mathops = CDBaseHelper('http://www.example.com/mathops')
>>> x = om.OMVariable('x'); a = om.OMVariable('a'); b = om.OMVariable('b'); c = om.OMVariable('c')
>>> arith1 = cd.arith1; relation1 = cd.relation1; multiops = mathops.multiops

>>> quadratic_formula = relation1.eq(
...     x,
...     arith1.divide(
...         multiops.plusminus(
...             arith1.unary_minus(b),
...             arith1.root(
...                 arith1.minus(
...                     arith1.power(
...                         b,
...                         2
...                     ),
...                     arith1.times(
...                         4,
...                         a,
...                         c
...                     )
...                 )
...             )
...         ),
...         arith1.times(
...             2,
...             a
...         )
...     )
... )

>>> print(quadratic_formula)
    OMApplication(
      elem=OMSymbol(name='eq', cd='relation1', cdbase='http://www.openmath.org/cd'),
      arguments=[
        OMVariable(name='x'),
        OMApplication(
          elem=OMSymbol(name='divide', cd='arith1', cdbase='http://www.openmath.org/cd'),
          arguments=[
            OMApplication(
              elem=OMSymbol(name='plusminus', cd='multiops', cdbase='http://www.example.com/mathops'),
              arguments=[
                OMApplication(
                  elem=OMSymbol(name='unary_minus', cd='arith1', cdbase='http://www.openmath.org/cd'),
                  arguments=[OMVariable(name='b')]),
                OMApplication(
                  elem=OMSymbol(name='root', cd='arith1', cdbase='http://www.openmath.org/cd'),
                  arguments=[OMApplication(
                    elem=OMSymbol(name='minus', cd='arith1', cdbase='http://www.openmath.org/cd'),
                    arguments=[
                      OMApplication(
                        elem=OMSymbol(name='power', cd='arith1', cdbase='http://www.openmath.org/cd'),
                        arguments=[
                          OMVariable(name='b'),
                          OMInteger(integer=2)]),
                      OMApplication(
                        elem=OMSymbol(name='times', cd='arith1', cdbase='http://www.openmath.org/cd'),
                        arguments=[
                          OMInteger(integer=4),
                          OMVariable(name='a'),
                          OMVariable(name='c')])])])]),
            OMApplication(
              elem=OMSymbol(name='times', cd='arith1', cdbase='http://www.openmath.org/cd'),
              arguments=[
                OMInteger(integer=2),
                OMVariable(name='a')])])])

Content Dictionary Base::

    >>> openmath_org = CDBaseHelper('http://www.openmath.org')
    >>> openmath_org
    CDBaseHelper('http://www.openmath.org')
    
    >>> openmath_cd = openmath_org / 'cd'
    >>> openmath_cd
    CDBaseHelper('http://www.openmath.org/cd')

Content Dictionary::

    >>> logic1 = openmath_cd.logic1
    >>> logic1
    CDHelper('http://www.openmath.org/cd', 'logic1')

    >>> logic2 = openmath_cd["logic1"]
    >>> logic2
    CDHelper('http://www.openmath.org/cd', 'logic1')

    >>> logic1 == logic2
    True

    >>> logic1.true
    OMSymbol(name='true', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')

    >>> logic2["false"]
    OMSymbol(name='false', cd='logic1', id=None, cdbase='http://www.openmath.org/cd')
"""

from . import openmath as om
import six
import inspect

class CDBaseHelper(object):
    """ Helper object pointing to a content dictionary base """

    def __init__(self, cdbase):
        self._cdbase = cdbase
        self._uri = cdbase
    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._cdbase == other._cdbase
    
    def __repr__(self):
        """ returns a unique representation of this object """
        return 'CDBaseHelper(%r)' % (self._cdbase)
    
    def __str__(self):
        """ returns a human-readable representation of this object """ 
        return 'CDBaseHelper(%s)' % (self._cdbase)

    def __div__(self, other):
        """ returns a new CDBaseHelper with other appended to the base url """
        return CDBaseHelper('%s/%s' % (self._cdbase, other))
    
    def __truediv__(self, other):
        """ same as self.__div__ """
        return self.__div__(other)

    def __getattr__(self, name):
        """ returns a CDHelper object with the given name and this as the base """
        
        return CDHelper(self._cdbase, name)
    
    def __getitem__(self, name):
        """ same as self.__getattr__ """
        return self.__getattr__(name)

class CDHelper(object):
    """ Helper object pointing to a content dictionary path """

    def __init__(self, cdbase, cd):
        self._cdbase = cdbase
        self._cd = cd
        self._uri = '%s?%s' % (cdbase, cd)
    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._cd == other._cd
    
    def __repr__(self):
        """ returns a unique representation of this object """
        return 'CDHelper(%r, %r)' % (self._cdbase, self._cd)
    
    def __str__(self):
        """ returns a human-readable representation of this object """ 
        return 'CDHelper(%s, %s)' % (self._cdbase, self._cd)
    
    def __getattr__(self, name):
        """ returns an OpenMath Symbol with self as the content dictonary and the given name """
        return OMSymbol(name=name, cd=self._cd, cdbase=self._cdbase)
    
    def __getitem__(self, name):
        """ same as self.__getattr__ """
        return self.__getattr__(name)

class WrappedHelper():
    """mixin for classes that wrap around an OM object to provide additional functionality"""
    def __init__(self, obj):
        self.obj = obj
    def toOM(self):
        return self.obj

class OMSymbol(om.OMSymbol):
    def __call__(self, *args, **kwargs):
        args = [interpretAsOpenMath(a) for a in args]
        return super(OMSymbol, self).__call__(*args, **kwargs)
    def __eq__(self, other):
        if isinstance(other, OMSymbol):
            return self.toOM() == other.toOM()
        else:
            return self.toOM() == other

    def toOM(self):
        return om.OMSymbol(name=self.name, cd=self.cd, id=self.id, cdbase=self.cdbase)


lambdaOM = CDBaseHelper("http://www.python.org")["lambda"] # .lambda not allowed because it's a reserved word

def interpretAsOpenMath(x):
    """tries to convert a Python object into an OpenMath object
    this is not a replacement for using a Converter for exporting Python objects
    instead, it is used conveniently building OM objects in DSL embedded in Python
    inparticular, it converts Python functions into OMBinding objects using lambdaOM as the binder"""
    
    if isinstance(x, OMSymbol):
        # wrapped OMSymbol -> unwrap
        return x.toOM()
    
    elif isinstance(x, om.OMAny):
        # already OM
        return x
    
    elif isinstance(x, six.integer_types):
        # integers -> OMI
        return om.OMInteger(x)
    
    elif isinstance(x, float):
        # floats -> OMF
        return om.OMFloat(x)

    elif isinstance(x, six.string_types):
        # strings -> OMSTR
        return om.OMString(x)
    
    elif isinstance(x, WrappedHelper):
        # wrapper -> wrapped object
        return x.toOM()
    
    elif inspect.isfunction(x):
        # function -> OMBIND(lambda,...)
        
        # get all the parameters of the function
        paramMap = inspect.signature(x).parameters
        params = [v for k, v in six.iteritems(paramMap)]
        
        # make sure that all of them are positional
        posArgKinds = [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]
        if not all([p.kind in posArgKinds for p in params]):
            raise CannotInterpretAsOpenMath("no sequence arguments allowed")
        
        # call the function with appropriate OMVariables
        paramsOM = [om.OMVariable(name=p.name) for p in params]
        bodyOM = interpretAsOpenMath(x(*paramsOM))

        return OMBinding(om.OMSymbol(name="lambda", cd="python", cdbase="http://python.org"), paramsOM, bodyOM)
    
    else:
        # fail
        raise CannotInterpretAsOpenMath("unknown kind of object: " + str(x))

class CannotInterpretAsOpenMath(Exception):
    """thrown when an object can not be interpreted as OpenMath """
    pass


__all__ = ["CDBaseHelper", "CDHelper", "WrappedHelper", "OMSymbol", "interpretAsOpenMath", "CannotInterpretAsOpenMath"]