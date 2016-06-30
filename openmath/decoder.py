""" Code used for decoding XML into an OpenMath object. """

from lxml import etree
from pkg_resources import resource_filename
from openmath import openmath as om, xml

def decode_xml(stream, validator=None):
    """
    """
    
    tree = etree.parse(stream)
    if validator is not None:
        validator.assertValid(tree)

    root = tree.getroot()
    v = root.get("version")
    if not v or v != "2.0":
        raise ValueError("Only OpenMath 2.0 is supported")

    return decode_om(root)
    
def decode_om(elem):
    """
    """
    
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
        attrs["omel"] = decode_om(elem[0])

    # Reference Objects
    elif issubclass(obj, om.OMReference):
        a2d("href")

    # Basic Objects
    elif issubclass(obj, om.OMInteger):
        attrs["integer"] = elem.text
    elif issubclass(obj, om.OMFloat):
        attrs["float"] = elem.get('dec')
    elif issubclass(obj, om.OMString):
        attrs["string"] = elem.text
    elif issubclass(obj, om.OMBytes):
        attr["bytes"] = base64.b64decode(elem.text)
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
        attrs["elem"] = decode_om(elem[0])
        attrs["arguments"] = list(map(decode_om, elem[1:]))
    elif issubclass(obj, om.OMAttribution):
        attrs["pairs"] = decode_om(elem[0])
        attrs["obj"] = decode_om(elem[1])
    elif issubclass(obj, om.OMAttributionPairs):
        attrs["pairs"] = [(decode_om(k), decode_om(v)) for k, v in zip(elem[::2], elem[1::2])]
    elif issubclass(obj, om.OMBinding):
        attrs["binder"] = decode_om(elem[0])
        attrs["vars"] = decode_om(elem[1])
        attrs["obj"] = decode_om(elem[2])
    elif issubclass(obj, om.OMBindVariables):
        attrs["vars"] = map(decode_om, elem[:])
    elif issubclass(obj, om.OMAttVar):
        attrs["pairs"] = decode_om(elem[0])
        attrs["obj"] = decode_om(elem[1])
    elif issubclass(obj, om.OMError):
        attrs["name"] = decode_om(elem[0])
        attrs["params"] = map(decode_om, elem[1:])
        
    else:
        raise TypeError("Expected OMAny, found %s." % obj.__name__)

    print (obj.__name__)
    return obj(**attrs)

def normative_validator():
    """ Load the normative validator provided by the OpenMath foundation. """

    relaxng_doc = etree.parse(resource_filename(__name__, 'openmath2.rng'))
    return etree.RelaxNG(relaxng_doc)
