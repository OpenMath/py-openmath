import unittest
from fractions import Fraction
from openmath.convert import *
from openmath import openmath as om, convert

class TestConvert(unittest.TestCase):
    def test_py_om_py(self):
        """ Convert from Python to OM and back. """

        testcases = [
            0, 1, -1, 2**100,
            True, False,
            0.0, 0.1, -0.1, float('inf'),
            complex(1,0), complex(0,1), complex(0,0), complex(1,1),
            "", "test",
            [], [1,2,3],
            set(), set([1,2,3]),
        ]
        for obj in testcases:
            conv = DefaultConverter.to_python(DefaultConverter.to_openmath(obj))
            self.assertEqual(type(obj), type(conv), "Converting %s" % obj.__class__.__name__)
            self.assertEqual(obj, conv, "Converting %s" % obj.__class__.__name__)
            self.assertRaises(ValueError, DefaultConverter.to_openmath, {})

    def test_register_str(self):
        def str_to_om(str):
            return om.OMString('Hello' + str)
        def str_to_py(om):
            return om.string + 'world'

        DefaultConverter.register(str, str_to_om, om.OMString, str_to_py)
        self.assertEqual(DefaultConverter.to_python(DefaultConverter.to_openmath(' ')), 'Hello world')

    def test_register_sym(self):
        DefaultConverter.register_to_python('hello1', 'hello', 'world')
        self.assertEqual(DefaultConverter.to_python(om.OMSymbol(cd='hello1', name='hello')), 'world')
        def echo(obj):
            return obj.name
        DefaultConverter.register_to_python('echo1', 'echo', echo)
        self.assertEqual(DefaultConverter.to_python(om.OMSymbol(cd='echo1', name='echo')), 'echo')

    def test_register_skip(self):
        def skip(obj):
            raise CannotConvertError()
        DefaultConverter.register_to_openmath(None, skip)
        self.assertEqual(DefaultConverter.to_openmath('hello'), om.OMString('hello'))

    def test_underscore(self):
        class test:
            def __openmath__(self):
                return om.OMInteger(1)
        self.assertEqual(DefaultConverter.to_python(DefaultConverter.to_openmath(test())), 1)

    def test_rational(self):
        def to_om_rat(obj):
            return om.OMApplication(om.OMSymbol('rational', cd='nums1'),
                                    map(DefaultConverter.to_openmath, [obj.numerator, obj.denominator]))
        def to_py_rat(obj):
            return Fraction(DefaultConverter.to_python(obj.arguments[0]), DefaultConverter.to_python(obj.arguments[1]))
        DefaultConverter.register(Fraction, to_om_rat, 'nums1', 'rational', to_py_rat)

        a = Fraction(10, 12)
        self.assertEqual(a, DefaultConverter.to_python(DefaultConverter.to_openmath(a)))

