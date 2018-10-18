from openmath import *
from inspect import *

#### syntactic sugar to use OpenMath as a DSL inside Python

#### helpers for OM (cdbase,cd,name) triples

class CDBaseHelper():
    """helper class to build CD references as cdbase.cd, see also CDHelper"""
    def __init__(self, cdbase):
        self.cdbase = cdbase
    def uri(self):
        return self.cdbase
    def __getattr__(self, cd):
        return CDHelper(self.cdbase, cd)

class CDHelper():
    """helper class to build OMS references as cdbase.cd.name, see also SymbolHelper"""
    def __init__(self, cdbase, cd):
        self.cdbase = cdbase
        self.cd = cd
    def uri(self):
        return self.cdbase + "?" + self.cd
    def __getattr__(self, name):
        return SymbolHelper(OMSymbol(cdbase=self.cdbase, cd=self.cd, name=name))

class WrappedHelper():
    """mixin for classes that wrap around an OM object to provide additional functionality"""
    def __init__(self, obj):
        self.obj = obj
    def toOM(self):
        return self.obj

class SymbolHelper(WrappedHelper):
    """wrapper around an OMS, built as cdbase.cd.name,
    callable to build OMAs as cdbase.cd.name(args)"""
    def uri(self):
        oms = self.toOM()
        return oms.cdbase + "?" + oms.cd + "?" + oms.name
    def __call__(self, *args):
        """builds an OMA with this instance as the function,
        arguments are passed through interpretAsOpenMath to apply some helpful conversions"""
        argsOM = [interpretAsOpenMath(x) for x in args]
        return OMApplication(elem=self.toOM(), arguments=argsOM)


#### interpret Python objects as OpenMath

class CannotInterpretAsOpenMath(Exception):
    """thrown by interpretAsOpenMath"""
    pass

pythonOM = CDBaseHelper("http://www.python.org")
pythonCD = pythonOM.python
lambdaOM = pythonCD.__getattr__("lambda") # .lambda not allowed because it's a reserved word

def interpretAsOpenMath(x):
    """tries to convert a Python object into an OpenMath object
    this is not a replacement for using a Converter for exporting Python objects
    instead, it is used conveniently building OM objects in DSL embedded in Python
    inparticular, it converts Python functions into OMBinding objects using lambdaOM as the binder"""
    if isinstance(x, OMAny):
        # already OM
        return x
    elif isinstance(x, int):
        # integers -> OMI
        return OMInteger(x)
    elif isinstance(x, str):
        # strings -> OMSTR
        return OMString(x)
    elif isinstance(x, WrappedHelper):
        # wrapper -> wrapped object
        return x.toOM()
    elif isfunction(x):
        # function -> OMBIND(lambda,...)
        sig = signature(x)
        paramMap = sig.parameters
        params = [paramMap[k] for k in paramMap.keys()]
        posArgKinds = [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
        if not(all([p.kind in posArgKinds for p in params])):
            raise CannotInterpretAsOpenMath("no sequence arguments allowed")
        paramsOM = [OMVariable(name=p.name) for p in params]
        body = x(*paramsOM)
        bodyOM = interpretAsOpenMath(body)
        return OMBinding(lambdaOM.toOM(), paramsOM, bodyOM)
    else:
        # fail
        raise CannotInterpretAsOpenMath("unknown kind of object: " + str(x))
