import unittest
import os.path

from lxml import etree

from tests.utils import expected
from openmath.encoder import encode_xml

from tests.utils import elements_equal


class TestEncoder(unittest.TestCase):
    def test_example(self):
        """ Tests the encoder based on an example. """

        with open(os.path.join(os.path.dirname(__file__), 'example.om')) as f:
            xmlnode = etree.fromstring(f.read())

        encoded = encode_xml(expected, 'om')
        print(etree.tostring(encoded, pretty_print=True).decode())

        # and check that they are as expected
        self.assertTrue(elements_equal(encoded, xmlnode), "Encoding an OpenMath object")
