""" Code used to encode an OpenMath object into XML. """
import base64

from lxml import etree
from lxml.builder import ElementMaker

from . import openmath as om
from . import xml

# Default element maker
default_E = ElementMaker(namespace=xml.openmath_ns,
                         nsmap={ None: xml.openmath_ns })

def encode_xml(obj, E=None):
    """ Encodes an OpenMath object as an XML node.

    :param obj: OpenMath object (or related item) to encode as XML.
    :type obj: OMAny

    :param ns: Namespace prefix to use for
        http://www.openmath.org/OpenMath", or None if default namespace.
    :type ns: str, None

    :return: The XML node representing the OpenMath data structure.
    :rtype: etree._Element
    """

    if E is None:
        E = default_E
    elif isinstance(E, str):
        E = ElementMaker(namespace=xml.openmath_ns,
                         nsmap={ E: xml.openmath_ns })

    name = ""
    attr = {}
    children = []

    if isinstance(obj, om.CDBaseAttribute) and obj.id is not None:
        attr["cdbase"] = obj.cdbase

    if isinstance(obj, om.CommonAttributes) and obj.id is not None:
        attr["id"] = obj.id

    # Wrapper object
    if isinstance(obj, om.OMObject):
        children.append(encode_xml(obj.omel, E))
        attr["version"] = obj.version

    # Derived Objects
    elif isinstance(obj, om.OMReference):
        attr["href"] = obj.href

    # Basic Objects
    elif isinstance(obj, om.OMInteger):
        children.append(str(obj.integer))
    elif isinstance(obj, om.OMFloat):
        attr["dec"] = obj.double
    elif isinstance(obj, om.OMString):
        if obj.string is not None:
            children.append(str(obj.string))
    elif isinstance(obj, om.OMBytes):
        children.append(base64.b64encode(obj.bytes).decode('ascii'))
    elif isinstance(obj, om.OMSymbol):
        attr["name"] = obj.name
        attr["cd"] = obj.cd
    elif isinstance(obj, om.OMVariable):
        attr["name"] = obj.name

    # Derived Elements
    elif isinstance(obj, om.OMForeign):
        attr["encoding"] = obj.encoding
        children.append(str(obj.obj))

    # Compound Elements
    elif isinstance(obj, om.OMApplication):
        children = [encode_xml(obj.elem, E)]
        children.extend(encode_xml(x, E) for x in obj.arguments)
    elif isinstance(obj, om.OMAttribution):
        children = [encode_xml(obj.pairs, E), encode_xml(obj.obj, E)]

    elif isinstance(obj, om.OMAttributionPairs):
        for (k, v) in obj.pairs:
            children.append(encode_xml(k, E))
            children.append(encode_xml(v, E))

    elif isinstance(obj, om.OMBinding):
        children = [
            encode_xml(obj.binder, E),
            encode_xml(obj.vars, E),
            encode_xml(obj.obj, E)
        ]
    elif isinstance(obj, om.OMBindVariables):
        children = [encode_xml(x, E) for x in obj.vars]
    elif isinstance(obj, om.OMAttVar):
        children = [encode_xml(obj.pairs, E), encode_xml(obj.obj, E)]
    elif isinstance(obj, om.OMError):
        children = [encode_xml(obj.name, E)]
        children.extend(encode_xml(x, E) for x in obj.params)
    else:
        raise TypeError("Expected obj to be of type OMAny, found %s." % obj.__class__.__name__)

    attr = dict((k,str(v)) for k, v in attr.items() if v is not None)

    return E(xml.object_to_tag(obj), *children, **attr)


def encode_bytes(obj, nsprefix=None):
    """ Encodes an OpenMath element into a string.

    :param obj: Object to encode as string.
    :type obj: OMAny

    :rtype: bytes
    """

    node = encode_xml(obj, nsprefix)
    return etree.tostring(node)

__all__ = ["encode_xml"]

