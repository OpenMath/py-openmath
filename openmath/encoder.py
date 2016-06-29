""" Code used to encode an OpenMath object into XML. """
import base64

from lxml import etree
from openmath.openmath import *

# Setup the OpenMath Namespace
# TODO: Find a better way to make the namespace.
openmath_ns = "http://www.openmath.org/OpenMath"
etree.register_namespace("om", openmath_ns)

def _om(t):
    """ Turns a tag into a tag with the OpenMath namespace.

    :param t: Tag to encode
    :type t: str

    :rtype: str
    """

    return "{%s}%s" % (openmath_ns, t)


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

    # Wrapper object
    if isinstance(obj, OMObject):
        return _make_element(_om("OMOBJ"), encode_xml(obj.omel), version=obj.version, id=obj.id, cdbase=obj.cdbase)

    # Derived Objects
    elif isinstance(obj, OMReference):
        return _make_element(_om("OMR"), href=str(obj.href), id=obj.id)

    # Basic Objects
    elif isinstance(obj, OMInteger):
        return _make_element(_om("OMI"), id=obj.id, **{"": str(obj.val)})
    elif isinstance(obj, OMFloat):
        return _make_element(_om("OMF"), dec={str(obj.val)}, id=obj.id)
    elif isinstance(obj, OMString):
        return _make_element(_om("OMSTR"), id=obj.id, **{"": obj.string})
    elif isinstance(obj, OMBytes):
        return _make_element(_om("OMB"), id=obj.id,
                             **{"": base64.b64encode(obj.bytes).encode(ascii)})
    elif isinstance(obj, OMSymbol):
        return _make_element(_om("OMS"), id=obj.id, name=obj.name, cd=obj.cd,
                             cdbase=obj.cdbase)
    elif isinstance(obj, OMVariable):
        return _make_element(_om("OMV"), id=obj.id, name=obj.name)

    # Derived Elements
    elif isinstance(obj, OMForeign):
        return _make_element("OMFOREIGN", id=obj.id, cdbase=obj.cdbase,
                             encoding=str(obj.encoding), **{"":str(obj.obj)})

    # TODO: Compound Elements

    elif not isinstance(obj, OMAny):
        raise NotImplementedError
    else:
        raise TypeError("Expected obj to be of type OMAny. ")

__all__ = ["encode_xml"]