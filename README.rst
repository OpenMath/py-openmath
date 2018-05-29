pyopenmath
==========

|Build Status| |Pypi|

Python `OpenMath
2.0 <http://www.openmath.org/standard/om20-2004-06-30/>`__
implementation.

Description
===========

`OpenMath <http://www.openmath.org/>`__ is an extensible standard for
representing the semantics of mathematical objects.

Installation
============

::
   
   pip install openmath

Usage
=====

This package provides an object implementation of OpenMath, and XML
parsing/serialization.

See `py-scscp <https://github.com/OpenMath/py-scscp>`__ for an example
of use.

XML Serialization
=================

The modules ``encoder`` and ``decoder`` provide XML de-serialization
for OpenMath objects.

::

   >>> from openmath import encoder, decoder, openmath as om
   >>> xml = encoder.encode_xml(om.OMString('hello world')); xml
   <Element {http://www.openmath.org/OpenMath}OMSTR at 0x7fcb3cd82708>
   >>> b = encoder.encode_bytes(om.OMString('hello world')); b
   b'<OMSTR xmlns="http://www.openmath.org/OpenMath">hello world</OMSTR>'
   >>> decoder.decode_xml(xml)
   OMString('hello world', id=None)
   >>> decoder.decode_bytes(b, snippet=True)
   OMString('hello world', id=None)

Conversions between Python and OpenMath
=======================================

This package provides facilities for easy conversions from Python to
OpenMath and back. The module ``convert`` contains a ``Converter`` class, which
is used to implements this functionality. For convenienve, an instance of this
class, ``DefaultConverter`` is provided.

The two functions ``to_python()`` and ``to_openmath()`` do the conversion as
their  names suggest, or raise a ``ValueError`` if no conversion is known.

By default, a ``Converter`` only implements conversions for basic Python types:

- bools,
- ints,
- floats,
- complex numbers,
- strings,
- bytes,
- lists (recursively),
- sets (recursively).

Furthermore, any object that defines an ``__openmath__(self)`` method
will have that method called by ``to_python``.

Finally, this class contains a mechanism for registering converters.

::

   >>> from fractions import Fraction
   >>> from openmath import openmath as om
   >>> from openmath.convert import DefaultConverter as converter
   >>> def to_om_rat(obj):
   ...     return om.OMApplication(om.OMSymbol('rational', cd='nums1'),
   ...                             list(map(converter.to_openmath, [obj.numerator, obj.denominator])))
   ...
   >>> def to_py_rat(obj):
   ...     return Fraction(converter.to_python(obj.arguments[0]), converter.to_python(obj.arguments[1]))
   ...
   >>> converter.register(Fraction, to_om_rat, 'nums1', 'rational', to_py_rat)
   >>> omobj = converter.to_openmath(Fraction(5, 6)); omobj
   OMApplication(OMSymbol('rational', 'nums1', id=None, cdbase=None), [OMInteger(5, id=None), OMInteger(6, id=None)], id=None, cdbase=None)
   >>> converter.to_python(omobj)
   Fraction(5, 6)


Contributing
============

The source code of this project can be found on `GitHub
<https://github.com/OpenMath/py-openmath>`__.  Please use GitHub
issues and pull requests to contribute to this project.

Credits
=======

This work is supported by `OpenDreamKit <http://opendreamkit.org/>`__.

License
=======

This work is licensed under the MIT License, for details see the LICENSE
file.

.. |Build Status| image:: https://travis-ci.org/OpenMath/py-openmath.svg?branch=master
   :target: https://travis-ci.org/OpenMath/py-openmath
.. |Pypi| image:: https://badge.fury.io/py/openmath.svg
    :target: https://badge.fury.io/py/openmath
   
