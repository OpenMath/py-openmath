""" Code used for decoding XML into an OpenMath object. """

from lxml import etree
from pkg_resources import resource_filename
from . import openmath as om
from . import xml
import base64
import io

def decode_bytes(xml, validator=None):
    """ Decodes a stream into an OpenMath object.

    :param xml: XML to decode.
    :type xml: bytes

    :param validator: Validator to use.

    :rtype: OMAny
    """
    return decode_stream(io.BytesIO(xml), validator)
    
def decode_stream(stream, validator=None):
    """ Decodes a stream into an OpenMath object.

    :param stream: Stream to decode.
    :type stream: Any

    :param validator: Validator to use.

    :rtype: OMAny
    """

    # TODO: Complete the docstring above

    
    tree = etree.parse(stream)
    if validator is not None:
        validator.assertValid(tree)

    root = tree.getroot()
    v = root.get("version")
    if not v or v != "2.0":
        raise ValueError("Only OpenMath 2.0 is supported")

    return decode_xml(root)

def decode_xml(elem, _in_bind = False):
    """ Decodes an XML element into an OpenMath object.

    :param elem: Element to decode.
    :type elem: etree._Element

    :param _in_bind: Internal flag used to indicate if we should decode within
    an OMBind.
    :type _in_bind: bool

    :rtype: OMAny
    """

    # TODO: Why are we using issubclass instead of isinstance?
    
    obj = xml.tag_to_object(elem.tag)
    attrs = {}
    
    def a2d(*props):
        for p in props:
            attrs[p] = elem.get(p)
    
    if issubclass(obj, om.CommonAttributes):
        a2d("id")
    if issubclass(obj, om.CDBaseAttribute):
        a2d("cdbase")

    # Root Object
    if issubclass(obj, om.OMObject):
        a2d("version")
        attrs["omel"] = decode_xml(elem[0])

    # Reference Objects
    elif issubclass(obj, om.OMReference):
        a2d("href")

    # Basic Objects
    elif issubclass(obj, om.OMInteger):
        attrs["integer"] = int(elem.text)
    elif issubclass(obj, om.OMFloat):
        # TODO: Support Hex
        attrs["double"] = float(elem.get('dec'))
    elif issubclass(obj, om.OMString):
        attrs["string"] = elem.text
    elif issubclass(obj, om.OMBytes):
        try:
            attrs["bytes"] = base64.b64decode(elem.text)
        except TypeError:
            attrs["bytes"] = base64.b64decode(bytes(elem.text, "ascii"))
    elif issubclass(obj, om.OMSymbol):
        a2d("name", "cd")
    elif issubclass(obj, om.OMVariable):
        a2d("name")

    # Derived Elements
    elif issubclass(obj, om.OMForeign):
        attrs["obj"] = elem.text
        a2d("encoding")

    # Compound Elements
    elif issubclass(obj, om.OMApplication):
        attrs["elem"] = decode_xml(elem[0])
        attrs["arguments"] = list(map(decode_xml, elem[1:]))
    elif issubclass(obj, om.OMAttribution):
        attrs["pairs"] = decode_xml(elem[0])
        attrs["obj"] = decode_xml(elem[1])
    elif issubclass(obj, om.OMAttributionPairs):
        if not _in_bind:
            attrs["pairs"] = [(decode_xml(k), decode_xml(v)) for k, v in zip(elem[::2], elem[1::2])]
        else:
            obj = om.OMAttVar
            attrs["pairs"] = decode_xml(elem[0], True)
            attrs["obj"] = decode_xml(elem[1], True)
    elif issubclass(obj, om.OMBinding):
        attrs["binder"] = decode_xml(elem[0])
        attrs["vars"] = decode_xml(elem[1])
        attrs["obj"] = decode_xml(elem[2])
    elif issubclass(obj, om.OMBindVariables):
        attrs["vars"] = list(map(lambda x:decode_xml(x, True), elem[:]))
    elif issubclass(obj, om.OMError):
        attrs["name"] = decode_xml(elem[0])
        attrs["params"] = list(map(decode_xml, elem[1:]))
        
    else:
        raise TypeError("Expected OMAny, found %s." % obj.__name__)

    return obj(**attrs)

def decode_xml_binding():
    pass

def normative_validator():
    """ Load the normative validator provided by the OpenMath foundation. """

    relaxng_doc = etree.parse(resource_filename(__name__, 'openmath2.rng'))
    return etree.RelaxNG(relaxng_doc)
