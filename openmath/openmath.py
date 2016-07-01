""" Contains a Data-structure for OpenMath and related objects. """
from case_class import AbstractCaseClass


class OMAny(AbstractCaseClass):
    """ Class for all OpenMath related objects. """

    pass


class CDBaseAttribute(OMAny, AbstractCaseClass):
    """ Mixin for OpenMath Objects with a cdbase attribute. """

    def __init__(self, cdbase):
        """ Creates a new CDBaseAttribute() instance.

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        # TODO: Think about using a URI class
        self.__cdbase = str(cdbase) if cdbase is not None else None

    @property
    def cdbase(self):
        """ Returns the content directory base URI for this object.

        :rtype: str
        """

        return self.__cdbase


class CommonAttributes(OMAny, AbstractCaseClass):
    """ Mixin for OpenMath Objects with common attributes. """

    def __init__(self, id=None):
        """ Creates a new CommonAttributes() instance.

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        self.__id = str(id) if id is not None else None

    @property
    def id(self):
        """ Returns the identifier to be used for structure sharing.

        :rtype: str
        """

        return self.__id


class CompoundAttributes(CommonAttributes, CDBaseAttribute, AbstractCaseClass):
    """ Mixin for OpenMath objects with compound attributes. """

    def __init__(self, id=None, cdbase=None):
        """ Creates a new CommonAttribute instance.

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        CommonAttributes.__init__(self, id)
        CDBaseAttribute.__init__(self, cdbase)


class OMAnyVal(OMAny, AbstractCaseClass):
    """ Shared Class for OpenMath Expressions + OpenMath Derived Objects. """

    pass


class OMObject(OMAnyVal, CompoundAttributes):
    """ Represents a single OpenMath object. """

    def __init__(self, omel, version=None, id=None, cdbase=None):
        """ Creates a new OMObject() instance.

        :param omel: Element that is contained in this OpenMath object.
        :type omel: OMExpression

        :param version: Version of this OpenMath object. Should be 2.0 in most
        cases.
        :param version: str

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """
        CompoundAttributes.__init__(self, id, cdbase)

        self.__omel = omel
        self.__version = str(version) if version is not None else "2.0"

    @property
    def omel(self):
        """ Returns the OpenMath element wrapped by this object.

        :rtype: OMExpression
        """

        return self.__omel

    @property
    def version(self):
        """ Returns the Version of this OpenMath element. Usually '2.0'.

        :rtype: str
        """

        return self.__version


class OMExpression(OMAnyVal, AbstractCaseClass):
    """ Base class for all OpenMath Expressions (i.e. proper objects
    according to the specification). """

    pass


class OMReference(OMExpression, CommonAttributes):
    """ An OpenMath reference. """

    def __init__(self, href, id=None):
        """ Creates a new OMReference() instance.

        :param href: URI pointing to the element being referenced.
        :type href: str

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMReference, self).__init__(id)

        # TODO: Think about using URI class here
        self.__href = str(href)

    @property
    def href(self):
        """ Returns the link to the referenced object.

        :rtype: str
        """

        return self.__href


class OMBasicElement(OMAny, AbstractCaseClass):
    """ Basic OpenMath objects (section 2.1.1). """
    pass


class OMInteger(OMBasicElement, CommonAttributes):
    """ An OpenMath integer. """

    def __init__(self, integer, id=None):
        """ Creates a new OMInteger() instance.

        :param integer: Integer wrapped by this OMInteger() instance.
        :type integer: int

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMInteger, self).__init__(id)

        self.__integer = int(integer)

    @property
    def integer(self):
        """ Returns the integer wrapped by this OMInteger().

        :rtype: int
        """

        return self.__integer


class OMFloat(OMBasicElement, CommonAttributes):
    """ An OpenMath double. """

    def __init__(self, double, id=None):
        """ Creates a new OMFloat() instance.

        :param double: Double-precision floating point number wrapped by this
        OMFloat() instance.
        :type double: float

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMFloat, self).__init__(id)

        self.__double = float(double)

    @property
    def double(self):
        """ Returns the double-precision floating point number wrapped by this
        OMFloat() instance. """

        return self.__double


class OMString(OMBasicElement, CommonAttributes):
    """ An OpenMath string. """

    def __init__(self, string, id=None):
        """ Creates a new OMString() instance.

        :param string: String value wrapped by this OMString() instance.
        :type string: str

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMString, self).__init__(id)

        self.__string = string

    @property
    def string(self):
        """ Returns the string wrapped by this OMString() instance.

        :rtype: str
        """

        return self.__string


class OMBytes(OMBasicElement, CommonAttributes):
    """ An OpenMath list of bytes. """

    def __init__(self, bytes, id=None):
        """ Creates a new OMBytes() instance.

        :param bytes: List of bytes wrapped by this OMBytes() list.
        :type bytes: list

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMBytes, self).__init__(id)

        self.__bytes = bytes
    
    @property
    def bytes(self):
        """ Returns the list of bytes wrapped by this OMBytes() instance.

        :rtype: list
        """
        
        return self.__bytes


class OMSymbol(OMBasicElement, CommonAttributes, CDBaseAttribute):
    """ An OpenMath symbol. """

    def __init__(self, name, cd, id=None, cdbase=None):
        """ Creates a new OMSymbol instance().

        :param name: Name of this OpenMath Symbol.
        :type name: str

        :param cd: Content Directory that this OMSymbol comes from.
        :type cd: str

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMSymbol, self).__init__(id)
        CDBaseAttribute.__init__(self, cdbase)

        # TODO: Verify if they match the regular expression?
        self.__name = str(name)
        self.__cd = str(cd)

    @property
    def name(self):
        """ Returns the name of this Symbol.

        :rtype: str
        """

        return self.__name

    @property
    def cd(self):
        """ Returns the Content Directory this Symbol comes from.

        :rtype: str
        """

        return self.__cd


class OMVariable(OMBasicElement, CommonAttributes):
    """ An OpenMath variable. """

    def __init__(self, name, id=None):
        """ Creates a new OMVariable() instance.

        :param name: Name of the Variable.
        :type name: str
        """

        super(OMVariable, self).__init__(id)

        # TODO: Check if we match the regex here?
        self.__name = str(name)

    @property
    def name(self):
        """ Returns the name of this OMVariable().

        :rtype: str
        """

        return self.__name


class OMDerivedElement(OMAnyVal, AbstractCaseClass):
    """ Derived OpenMath objects (section 2.1.2). """

    pass


class OMForeign(OMDerivedElement, CompoundAttributes):
    """ An OpenMath Foreign Object. """
    def __init__(self, obj, encoding, id=None, cdbase=None):
        """ Creates a new OMForeign() object.

        :param obj: Foreign Object contained.
        :param obj: obj

        :param encoding: Encoding of this OpenMath object.
        :param encoding: str

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMForeign, self).__init__(id, cdbase)

        self.__obj = obj
        self.__encoding = str(encoding) if encoding is not None else None

    @property
    def obj(self):
        """ Returns the foreign object contained in this OMForeign() instance.

        :rtype: obj
        """

        return self.__obj

    @property
    def encoding(self):
        """ Returns the encoding used by this OMForeign() instance.

        :rtype str:
        """

        return self.__encoding


class OMCompoundElement(OMExpression, AbstractCaseClass):
    """ Compound OpenMath objects (section 2.1.3). """
    pass


class OMApplication(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Application Object. """

    def __init__(self, elem, arguments, id=None, cdbase=None):
        """ Creates a new OMApplication() object.

        :param elem: Element that is being applied to.
        :type elem: OMExpression

        :param arguments: List of arguments that are being applied.
        :type arguments: list

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMApplication, self).__init__(id, cdbase)

        self.__elem = elem
        self.__arguments = list(arguments)

    @property
    def elem(self):
        """ Returns the element that is being applied to.

        :rtype: OMExpression
        """

        return self.__elem

    @property
    def arguments(self):
        """ Returns the list of arguments that are being applied.

        :rtype: list
        """

        return self.__arguments


class OMAttribution(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Attribution Object. """

    def __init__(self, pairs, obj, id=None, cdbase=None):
        """ Creates a new OMAttribution() instance.

        :param pairs: Pairs of this OMAttribution object.
        :type pairs: OMAttributionPairs

        :param obj: Object that is being attributed.
        :type obj: OMExpression

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """
        super(OMAttribution, self).__init__(id, cdbase)

        self.__pairs = pairs
        self.__obj = obj

    @property
    def pairs(self):
        """ Returns the pairs of this OMAttribution object.

        :rtype: OMAttributionPairs
        """

        return self.__pairs

    @property
    def obj(self):
        """ Returns the object that is being attributed.

        :rtype: OMExpression
        """

        return self.__obj


class OMAttributionPairs(CompoundAttributes):
    """ List of Attribution pairs. """

    def __init__(self, pairs, id=None, cdbase=None):
        """ Creates a new OMAttributionPairs() instance.

        :param pairs: List of (OMSymbol, OMAnyVal) tuples.
        :type pairs: list

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMAttributionPairs, self).__init__(id, cdbase)

        self.__pairs = list(pairs)

    @property
    def pairs(self):
        """ Returns the list of (OMSymbol, OMAnyVal) tuples.

        :rtype: list
        """

        return self.__pairs


class OMBinding(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Binding. """

    def __init__(self, binder, vars, obj, id=None, cdbase=None):
        """ Creates a new OMBinding() object.

        :param binder: Binder being used to bind variables.
        :type binder: OMExpression

        :param vars: Variables being bound.
        :type vars: OMBindVariables

        :param obj: Object the variables are bound in.
        :param obj: OMExpression

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMBinding, self).__init__(id, cdbase)

        self.__binder = binder
        self.__vars = vars
        self.__obj = obj
    
    @property
    def binder(self):
        """ Returns the binder being used to bind variables.

        :rtype: OMExpression
        """
        
        return self.__binder

    @property
    def vars(self):
        """ Returns the Variable that are being bound.

        :rtype: OMBindVariables
        """

        return self.__vars

    @property
    def obj(self):
        """ Returns the object the variables are bound in.

        :rtype: OMExpression
        """

        return self.__obj


class OMAttVar(CommonAttributes):
    """ Represents an attributed variable. """

    def __init__(self, pairs, obj, id=None):
        """ Creates a new OMAttVar() object.

        :param pairs: Pairs of this OMAttVar object.
        :type pairs: OMAttributionPairs

        :param obj: Object that is being attributed.
        :type obj: OMExpression

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMAttVar, self).__init__(id)

        self.__pairs = pairs
        self.__obj = obj

    @property
    def pairs(self):
        """ Returns the pairs of this OMAttVar object.

        :rtype: OMAttributionPairs
        """

        return self.__pairs

    @property
    def obj(self):
        """ Returns the object that is being attributed.

        :rtype: OMExpression
        """

        return self.__obj


class OMBindVariables(CommonAttributes):
    """ List of OpenMath bound variables. """

    def __init__(self, vars, id=None):
        """ Creates a new OMBindVariables() instance.

        :param vars: List of OMVariable or OMAttVar instances.
        :type vars: list

        :param id: Identifier to use for Structure sharing.
        :type id: str
        """

        super(OMBindVariables, self).__init__(id)

        self.__vars = list(vars)

    @property
    def vars(self):
        """ Returns the list of OMVar instances.

        :rtype: list
        """

        return self.__vars


class OMError(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Error. """

    def __init__(self, name, params, id=None, cdbase=None):
        """ Creates a new OMError() instance.

        :param name: OMSymbol() representing the name of this error.
        :type name: OMSymbol

        :param params: List of OMAnyVal instances representing the parameters
        for this instance.
        :type params: list

        :param id: Identifier to use for Structure sharing.
        :type id: str

        :param cdbase: Content Directory Base URI.
        :type cdbase: str
        """

        super(OMError, self).__init__(id, cdbase)

        self.__name = name
        self.__params = list(params)

    @property
    def name(self):
        """ Returns the name of this OMError().

        :rtype: OMSymbol
        """

        return self.__name

    @property
    def params(self):
        """ Returns the list of OMAnyVal() instances representing the
        parameters given to this OMError() instance.

        :rtype: list
        """
        return self.__params

__all__ = ["OMAny", "CDBaseAttribute", "CommonAttributes",
           "CompoundAttributes", "OMAnyVal", "OMObject", "OMExpression",
           "OMReference", "OMBasicElement", "OMInteger", "OMFloat", "OMString",
           "OMBytes", "OMSymbol", "OMVariable", "OMDerivedElement",
           "OMForeign", "OMCompoundElement", "OMApplication", "OMAttribution",
           "OMAttributionPairs", "OMBinding", "OMAttVar",
           "OMBindVariables", "OMError"]
