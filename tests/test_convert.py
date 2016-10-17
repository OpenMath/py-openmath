import unittest

from openmath.convert import *

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
            conv = to_python(to_openmath(obj))
            self.assertEqual(type(obj), type(conv), "Converting %s" % obj.__class__.__name__)
            self.assertEqual(obj, conv, "Converting %s" % obj.__class__.__name__)
            self.assertRaises(ValueError, to_openmath, {})
