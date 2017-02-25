import unittest
import os.path

from lxml import etree
from tests.utils import expected

from openmath.decoder import decode_xml, decode_bytes
from openmath import openmath as om

class TestDecoder(unittest.TestCase):
    def test_example(self):
        """ Tests the decoder based on an example. """

        # try to parse the xml
        with open(os.path.join(os.path.dirname(__file__), 'example.om')) as f:
            xmlnode = etree.fromstring(f.read())

        omnode = decode_xml(xmlnode)

        # and check that they are as expected
        self.assertEqual(omnode, expected, "Decoding an OpenMath object")

    def test_snippet(self):
        """ Test that snippets are parsed correctly """
        str = decode_bytes(b'<OMSTR>hello world</OMSTR>', snippet=True)
        self.assertEqual(str, om.OMString('hello world'))
        with self.assertRaises(ValueError):
            decode_bytes(b'<OMSTR>hello world</OMSTR>')
