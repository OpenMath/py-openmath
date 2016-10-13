""" Code used to encode an OpenMath object into XML. """
import base64

from lxml import etree

from . import openmath as om
from . import xml

# Setup the OpenMath Namespace
# TODO: Find a better way to make the namespace.
etree.register_namespace("om", xml.openmath_ns)

def _om(t):
    """ Turns a tag into a tag with the OpenMath namespace.

    :param t: Tag to encode
    :type t: str

    :rtype: str
    """

    return "{%s}%s" % (xml.openmath_ns, t)


def _make_element(tag, *children, **attributes):
    """Makes a new XML Element.

    :param tag: The name of the tag to create.
    :type tag: str

    :param children: A list of children to create. Each child should be of one of
            the following forms:

            1. tag
            2. (tag,)
            3. (tag, children)
            4. (tag, children, attributes)
    :type children: list

    :param attributes: List of attributes to create. Use the empty attribute
    for text content. If an attribute is None, then it is omitted.
    :type attributes: dict
    """

    # Create the element first.

    # if it is already an element
    if isinstance(tag, etree._Element):
        me = tag

    # if it is a tuple, it should be (tag_name, text)
    elif isinstance(tag, tuple):
        me = etree.Element(tag[0])
        me.text = str(tag[1])
    # else it is just a tag name
    else:
        me = etree.Element(tag)

    # set the attributes
    for (a, v) in attributes.items():
        if v is not None:
            if a == "":
                me.text = str(v)
            else:
                me.set(a, str(v))

    # now iterate through the children
    for c in children:

        # take all the different cases into account
        if isinstance(c, tuple):
            if len(c) == 1:
                (ct,) = c
                (cc, ca) = ([], {})
            elif len(c) == 2:
                (ct,cc) = c
                ca = {}
            else:
                (ct,cc,ca) = c
        else:
            ct = c
            (cc, ca) = ([], {})

        # and add a proper child element
        me.append(_make_element(c, *cc, **ca))

    # finally return the generated element
    return me


def encode_xml(obj):
    """ Encodes an OpenMath object as an XML node.

    :param obj: OpenMath object (or related item) to encode as XML.
    :type obj: OMAny

    :return: The XML node representing the OpenMath data structure.
    :rtype: etree._Element
    """

    name = ""
    attr = {}
    children = []

    if isinstance(obj, om.CDBaseAttribute):
        attr["cdbase"] = obj.cdbase

    if isinstance(obj, om.CommonAttributes):
        attr["id"] = obj.id

    # Wrapper object
    if isinstance(obj, om.OMObject):
        name = "OMOBJ"
        children.append(encode_xml(obj.omel))
        attr["version"] = obj.version

    # Derived Objects
    elif isinstance(obj, om.OMReference):
        name = "OMR"
        attr["href"] = obj.href

    # Basic Objects
    elif isinstance(obj, om.OMInteger):
        name = "OMI"
        attr[""] = obj.integer
    elif isinstance(obj, om.OMFloat):
        name = "OMF"
        attr["dec"] = obj.double
    elif isinstance(obj, om.OMString):
        name = "OMSTR"
        attr[""] = obj.string
    elif isinstance(obj, om.OMBytes):
        name = "OMB"
        attr[""] = base64.b64encode(obj.bytes).decode('ascii')
    elif isinstance(obj, om.OMSymbol):
        name = "OMS"
        attr["name"] = obj.name
        attr["cd"] = obj.cd
    elif isinstance(obj, om.OMVariable):
        name = "OMV"
        attr["name"] = obj.name

    # Derived Elements
    elif isinstance(obj, om.OMForeign):
        name = "OMFOREIGN"
        attr["encoding"] = obj.encoding
        attr[""] = obj.obj

    # Compound Elements
    elif isinstance(obj, om.OMApplication):
        name = "OMA"
        children = [encode_xml(obj.elem)]
        children.extend(map(encode_xml, obj.arguments))
    elif isinstance(obj, om.OMAttribution):
        name = "OMATTR"
        children = [encode_xml(obj.pairs), encode_xml(obj.obj)]

    elif isinstance(obj, om.OMAttributionPairs):
        name = "OMATP"
        children = []

        for (k, v) in obj.pairs:
            children.append(encode_xml(k))
            children.append(encode_xml(v))

    elif isinstance(obj, om.OMBinding):
        name = "OMBIND"
        children = [
            encode_xml(obj.binder),
            encode_xml(obj.vars),
            encode_xml(obj.obj)
        ]
    elif isinstance(obj, om.OMBindVariables):
        name = "OMBVAR"
        children = list(map(encode_xml, obj.vars))
    elif isinstance(obj, om.OMAttVar):
        name = "OMATTR"
        children = [encode_xml(obj.pairs), encode_xml(obj.obj)]
    elif isinstance(obj, om.OMError):
        name = "OME"
        children = [encode_xml(obj.name)]
        children.extend(map(encode_xml, obj.params))
    else:
        raise TypeError("Expected obj to be of type OMAny, found %s." % obj.__class__.__name__)

    return _make_element(_om(name), *children, **attr)


def encode_bytes(obj):
    """ Encodes an OpenMath element into a string.

    :param obj: Object to encode as string.
    :type obj: OMAny

    :rtype: bytes
    """

    node = encode_xml(obj)
    return etree.tostring(node)

__all__ = ["encode_xml"]

