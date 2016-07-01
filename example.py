from openmath.openmath import OMObject, OMInteger
from openmath.encoder import encode_xml
from openmath.decoder import decode_xml

from lxml import etree

with open("tests/example.om") as f:
    xml = etree.fromstring(str(f.read()))

# try to decode the xml
node = decode_xml(xml)

# print it
print(node)

# check if encode / decode works properly.
print(decode_xml(encode_xml(node)) == node)


obj = OMObject(OMInteger(42))
print(etree.tostring(encode_xml(obj)))