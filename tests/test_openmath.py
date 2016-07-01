import unittest

from lxml import etree

from openmath.openmath import *
from openmath.encoder import encode_xml
from openmath.decoder import decode_xml
from tests.utils import object_examples, elements_equal


class TestReCode(unittest.TestCase):

    def test_re_encode(self):
        """ Test re-encoding objects working properly. """

        for (om, xml) in object_examples:
            omx = encode_xml(decode_xml(encode_xml(om)))
            xn = etree.fromstring(xml)

            self.assertTrue(elements_equal(omx, xn), 'encode(decode(encode(om))) === xml')

    def test_re_decode(self):
        """ Test re-decoding objects working properly. """

        for (om, xml) in object_examples:
            xn = decode_xml(encode_xml(decode_xml(etree.fromstring(xml))))

            self.assertEqual(om, xn, 'decode(encode(decode(xml))) === om')
