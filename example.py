from openmath.openmath import OMObject, OMInteger
from openmath.encoder import encode_xml

from lxml import etree

obj = OMObject(OMInteger(42))
print(etree.tostring(encode_xml(obj)))