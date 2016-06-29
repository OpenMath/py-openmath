

class OMAny(object):
    """ Class for all OpenMath related objects. """

    pass


class CDBaseAttribute(OMAny):
    """ Mixin for OpenMath Objects with a cdbase attribute. """

    def __init__(self, cdbase):
        self.cdbase = cdbase


class CommonAttributes(OMAny):
    """ Mixin for OpenMath Objects with common attributes. """

    def __init__(self, id):
        self.id = id


class CompoundAttributes(OMAny, CommonAttributes, CDBaseAttribute):
    """ Mixin for OpenMath objects with compound attributes. """
    def __init__(self, id, cdbase):

        CommonAttributes.__init__(self, id)
        CDBaseAttribute.__init__(self, cdbase)


class OMAnyVal(OMAny):
    """ Shared Class for OpenMath Expressions + OpenMath Derived Objects. """

    pass


class OMObject(OMAnyVal, CompoundAttributes):
    """ Represents a single OpenMath object. """

    def __init__(self, omel, version, id, cdbase):
        CompoundAttributes.__init__(self, id, cdbase)

        self.omel = omel
        self.version = version


class OMExpression(OMAnyVal):
    """ Base class for all OpenMath Expressions (i.e. proper objects
    according to the specification). """
    pass


class OMReference(OMExpression, CommonAttributes):
    """ An OpenMath reference. """

    def __init__(self, href, id):
        super(OMReference, self).__init__(id)

        self.href = href


class OMBasicElement(OMReference):
    """ Basic OpenMath objects (section 2.1.1). """
    pass


class OMInteger(OMBasicElement, CommonAttributes):
    """ An OpenMath integer. """
    def __init__(self, val, id):

        super(OMInteger, self).__init__(id)
        self.val = val


class OMFloat(OMBasicElement, CommonAttributes):
    """ An OpenMath double. """

    def __init__(self, val, id):
        super(OMFloat, self).__init__(id)
        self.val = val


class OMString(OMBasicElement, CommonAttributes):
    """ An OpenMath string. """

    def __init__(self, string, id):
        super(OMString, self).__init__(id)
        self.string = string


class OMBytes(OMBasicElement, CommonAttributes):
    """ An OpenMath list of bytes. """

    def __init__(self, bytes, id):
        super(OMBytes, self).__init__(id)
        self.bytes = bytes


class OMSymbol(OMBasicElement, CommonAttributes, CDBaseAttribute):
    """ An OpenMath symbol. """

    def __init__(self, name, cd, id, cdbase):
        super(OMSymbol, self).__init__(id)
        CDBaseAttribute.__init__(self, cdbase)

        self.name = name
        self.cd = cd


class OMVariable(OMBasicElement, CommonAttributes):
    """ An OpenMath variable. """

    def __init__(self, name, id):
        super(OMVariable, self).__init__(id)

        self.name = name


class OMDerivedElement(OMAnyVal):
    """ Derived OpenMath objects (section 2.1.2). """
    pass


class OMForeign(OMDerivedElement, CompoundAttributes):
    """ An OpenMath Foreign Object. """
    def __init__(self, obj, encoding, id, cdbase):
        super(OMForeign, self).__init__(id, cdbase)

        self.obj = obj
        self.encoding = encoding


class OMCompoundElement(OMExpression):
    """ Compound OpenMath objects (section 2.1.3). """
    pass


class OMApplication(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Application Object. """

    def __init__(self, elem, arguments, id, cdbase):
        super(OMApplication, self).__init__(id, cdbase)
        self.elem = elem
        self.arguments = arguments


class OMAttribution(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Attribution Object. """

    def __init__(self, pairs, A, id, cdbase):
        super(OMAttribution, self).__init__(id, cdbase)
        self.pairs = pairs
        self.A = A

class OMAttributionPairs(OMAny, CompoundAttributes):
    """ List of Attribution pairs. """

    def __init__(self, pairs, id, cdbase):
        super(OMAttributionPairs, self).__init__(id, cdbase)
        self.pairs = pairs


class OMBinding(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Binding. """

    def __init__(self, B, vars, C, id, cdbase):
        super(OMBinding, self).__init__(id, cdbase)
        self.B = B
        self.vars = vars
        self.C = C

class OMVar(OMAny):
    """ Represents a Variable or Attributed Variable. """

    pass


class OMVarVar(OMVar):
    """ Represents a single bound variable. """

    def __init__(self, omv):
        self.omv = omv


class OMAttVar(OMVar, CommonAttributes):
    """ Represents an attributed variable. """

    def __init__(self, pairs, A, id):
        super(OMAttVar, self).__init__(id)

        self.pairs = pairs
        self.A = A


class OMBindVariables(OMAny, CommonAttributes):
    """ List of OpenMath bound variables. """

    def __init__(self, vars, id):
        super(OMBindVariables, self).__init__(id)

        self.vars = vars


class OMError(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Error. """

    def __init__(self, name, params, id, cdbase):
        super(OMError, self).__init__(id, cdbase)
        self.name = name
        self.params = params