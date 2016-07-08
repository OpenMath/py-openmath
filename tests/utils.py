from openmath.openmath import *
from lxml import etree


def elements_equal(e1, e2):
    """ Checks if two xml elements are equal.

    :param e1: First element to check.
    :type e1: etree._Element

    :param e2: Seconds element to check.
    :type e2: etree._Element

    Adapted from http://stackoverflow.com/a/24349916.

    :rtype: bool
    """

    if e1.tag != e2.tag:
        return False

    e1te = e1.text.strip() if e1.text is not None else ''
    e2te = e2.text.strip() if e2.text is not None else ''
    if e1te != e2te:
        return False

    e1ta = e1.tail.strip() if e1.tail is not None else ''
    e2ta = e2.tail.strip() if e2.tail is not None else ''
    if e1ta != e2ta:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False

    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

expected = OMObject(OMAttribution(OMAttributionPairs([(OMSymbol('call_id', 'scscp1', id=None, cdbase=None), OMString('symcomp.org:26133:18668:s2sYf1pg', id=None)), (OMSymbol('option_runtime', 'scscp1', id=None, cdbase=None), OMInteger(300000, id=None)), (OMSymbol('option_min_memory', 'scscp1', id=None, cdbase=None), OMInteger(40964, id=None)), (OMSymbol('option_max_memory', 'scscp1', id=None, cdbase=None), OMInteger(134217728, id=None)), (OMSymbol('option_debuglevel', 'scscp1', id=None, cdbase=None), OMInteger(2, id=None)), (OMSymbol('option_return_object', 'scscp1', id=None, cdbase=None), OMString(None, id=None))], id=None, cdbase=None), OMApplication(OMSymbol('procedure_call', 'scscp1', id=None, cdbase=None), [OMApplication(OMSymbol('GroupIdentificationService', 'scscp_transient_1', id=None, cdbase=None), [OMApplication(OMSymbol('group', 'group1', id=None, cdbase=None), [OMApplication(OMSymbol('permutation', 'permut1', id=None, cdbase=None), [OMInteger(2, id=None), OMInteger(3, id=None), OMInteger(1, id=None)], id=None, cdbase=None), OMApplication(OMSymbol('permutation', 'permut1', id=None, cdbase=None), [OMInteger(1, id=None), OMInteger(2, id=None), OMInteger(4, id=None), OMInteger(3, id=None)], id=None, cdbase=None)], id=None, cdbase=None)], id=None, cdbase=None)], id=None, cdbase=None), id=None), version='2.0', id=None, cdbase=None)

object_examples = [

    # OMObject
    (
        OMObject(OMInteger(1, None), '2.0', None, None),
        '<om:OMOBJ xmlns:om="http://www.openmath.org/OpenMath" version="2.0"><om:OMI>1</om:OMI></om:OMOBJ>'
    ),

    # building on this
    (
        OMReference('#test'),
        '<om:OMR xmlns:om="http://www.openmath.org/OpenMath" href="#test"/>'
    ),

    # Basic Objects
    (
        OMInteger(1),
        '<om:OMI xmlns:om="http://www.openmath.org/OpenMath">1</om:OMI>'
    ),
    (
        OMFloat(10.0),
        '<om:OMF xmlns:om="http://www.openmath.org/OpenMath" dec="10.0"/>'
    ),
    (
        OMString('test'),
        '<om:OMSTR xmlns:om="http://www.openmath.org/OpenMath">test</om:OMSTR>'
    ),
    (
        OMBytes(b'\x13'),
        '<om:OMB xmlns:om="http://www.openmath.org/OpenMath">Ew==</om:OMB>'
    ),
    (
        OMSymbol('hello', 'world', None, None),
        '<om:OMS xmlns:om="http://www.openmath.org/OpenMath" name="hello" cd="world"/>',
    ),
    (
        OMVariable('x', None),
        '<om:OMV xmlns:om="http://www.openmath.org/OpenMath" name="x"/>'
    ),
    (
        OMForeign('something', None),
        '<om:OMFOREIGN xmlns:om="http://www.openmath.org/OpenMath">something</om:OMFOREIGN>',
    ),
    (
        OMApplication(OMSymbol('sin', 'transc1'), [OMVariable('x')]),
        '<om:OMA xmlns:om="http://www.openmath.org/OpenMath"><om:OMS name="sin" cd="transc1"/><om:OMV name="x"/></om:OMA>'
    ),
    (
        OMBinding(OMSymbol('lambda', 'fns1'), OMBindVariables([
            OMVariable('x')
        ]), OMApplication(
            OMSymbol('sin', 'transc1'), [OMVariable('x')]
        )),
        '<om:OMBIND xmlns:om="http://www.openmath.org/OpenMath"><om:OMS name="lambda" cd="fns1"/><om:OMBVAR><om:OMV name="x"/></om:OMBVAR><om:OMA><om:OMS name="sin" cd="transc1"/><om:OMV name="x"/></om:OMA></om:OMBIND>'
    ),
    (
        OMAttribution(OMAttributionPairs([
            (OMSymbol('type', 'ecc'), OMSymbol('real', 'ecc'))
        ]), OMVariable('x')),
        '<om:OMATTR xmlns:om="http://www.openmath.org/OpenMath"><om:OMATP><om:OMS name="type" cd="ecc"/><om:OMS name="real" cd="ecc"/></om:OMATP><om:OMV name="x"/></om:OMATTR>',
    ),
    (
        OMError(OMSymbol('DivisionByZero', 'aritherror'),
                [
                    OMApplication(OMSymbol('divide', 'arith1'), [
                        OMVariable('x'),
                        OMInteger(0)
                    ])
                ]),
        '<om:OME xmlns:om="http://www.openmath.org/OpenMath"><om:OMS name="DivisionByZero" cd="aritherror"/><om:OMA><om:OMS name="divide" cd="arith1"/><om:OMV name="x"/><om:OMI>0</om:OMI></om:OMA></om:OME>'
    )
]

__all__ = ["elements_equal", "expected", "examples", "object_examples"]
