"""
Tests for basic validation checks.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest

from model_data import MappingDataNode, Notification
from model_data.validation import checks
from geomop_util import TextValue


def test_check_integer():
    input_type = dict(min=0, max=3)
    input_type_inf = dict(min=float('-inf'), max=float('inf'))

    assert checks.check_integer(3, input_type_inf) is True
    assert checks.check_integer(-2, input_type_inf) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_integer(2.5, input_type)
    assert excinfo.value.name == 'ValidationTypeError'
    with pytest.raises(Notification) as excinfo:
        checks.check_integer("3", input_type)
    assert excinfo.value.name == 'ValidationTypeError'
    with pytest.raises(Notification) as excinfo:
        checks.check_integer({}, input_type)
    assert excinfo.value.name == 'ValidationTypeError'
    with pytest.raises(Notification) as excinfo:
        checks.check_integer([], input_type)
    assert excinfo.value.name == 'ValidationTypeError'
    with pytest.raises(Notification) as excinfo:
        checks.check_integer(True, input_type)
    assert excinfo.value.name == 'ValidationTypeError'

    assert checks.check_integer(3, input_type) is True
    assert checks.check_integer(2, input_type) is True
    assert checks.check_integer(0, input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_integer(-1, input_type)
    assert excinfo.value.name == 'ValueTooSmall'

    with pytest.raises(Notification) as excinfo:
        checks.check_integer(5, input_type)
    assert excinfo.value.name == 'ValueTooBig'


def test_check_double():
    input_type = dict(min=0, max=3.14)
    input_type_inf = dict(min=float('-inf'), max=float('inf'))

    assert checks.check_double(3.14, input_type_inf) is True
    assert checks.check_double(-2, input_type_inf) is True  # accepts int

    with pytest.raises(Notification) as excinfo:
        checks.check_double("3.14", input_type)
    assert excinfo.value.name == 'ValidationTypeError'
    with pytest.raises(Notification) as excinfo:
        checks.check_integer(True, input_type)
    assert excinfo.value.name == 'ValidationTypeError'

    assert checks.check_double(3.14, input_type) is True
    assert checks.check_double(2.5, input_type) is True
    assert checks.check_double(0, input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_double(-1.3, input_type)
    assert excinfo.value.name == 'ValueTooSmall'

    with pytest.raises(Notification) as excinfo:
        checks.check_double(5, input_type)
    assert excinfo.value.name == 'ValueTooBig'


def test_check_bool():
    input_type = dict()
    assert checks.check_bool(True, input_type) is True
    assert checks.check_bool(False, input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_bool({}, input_type)
    assert excinfo.value.name == 'ValidationTypeError'


def test_check_string():
    input_type = dict()
    assert checks.check_string("abc", input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_string({}, input_type)
    assert excinfo.value.name == 'ValidationTypeError'


def test_check_selection():
    input_type = dict(values={'a': 1, 'b': 2, 'c': 3}, name="MySelection")

    assert checks.check_selection('a', input_type) is True
    assert checks.check_selection('b', input_type) is True
    assert checks.check_selection('c', input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_selection('d', input_type)
    assert excinfo.value.name == 'InvalidSelectionOption'


def test_check_filename():
    input_type = dict()
    assert checks.check_filename("abc", input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_filename({}, input_type)
    assert excinfo.value.name == 'ValidationTypeError'


def test_check_array():
    input_type = dict(min=1, max=5)
    input_type_inf = dict(min=0, max=float('inf'))
    assert checks.check_array([], input_type_inf) is True
    assert checks.check_array([None]*2, input_type) is True
    assert checks.check_array([None]*1, input_type) is True
    assert checks.check_array([None]*5, input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_array(None, input_type)
    assert excinfo.value.name == 'ValidationTypeError'

    with pytest.raises(Notification) as excinfo:
        checks.check_array([], input_type)
    assert excinfo.value.name == 'NotEnoughItems'

    with pytest.raises(Notification) as excinfo:
        checks.check_array([None]*6, input_type)
    assert excinfo.value.name == 'TooManyItems'


def test_check_record_key():
    keys = {
        'a1': {'default': {'type': 'obligatory'}},
        'a2': {'default': {'type': 'obligatory'}},
        'b': {'default': {'type': 'value at declaration'}},
        'c': {'default': {'type': 'value at read time'}},
        'd': {'default': {'type': 'optional'}}
    }
    input_type = dict(keys=keys, name='MyRecord')

    assert checks.check_record_key(['a1'], 'a1', input_type) is True
    assert checks.check_record_key(['a1'], 'b', input_type) is True
    assert checks.check_record_key(['a1'], 'c', input_type) is True
    assert checks.check_record_key(['a1'], 'd', input_type) is True

    with pytest.raises(Notification) as excinfo:
        checks.check_record_key('unknown', 'unknown', input_type)
    assert excinfo.value.name == 'UnknownRecordKey'

    with pytest.raises(Notification) as excinfo:
        checks.check_record_key(['a1'], 'a2', input_type)
    assert excinfo.value.name == 'MissingObligatoryKey'


def test_check_abstractrecord():
    type1 = dict(name='type1')
    type2 = dict(name='type2')
    type3 = dict(name='type3')
    input_type = dict(default_descendant=type1, implementations={
        'type1': type1, 'type2': type2, 'type3': type3}, name='MyAbstract')
    input_type_no_default = dict(implementations={'type1': type1,
                                                  'type2': type2,
                                                  'type3': type3})
    node = MappingDataNode()
    node.type = TextValue()
    node.type.value = 'type2'

    assert checks.get_abstractrecord_type(node, input_type) == type2
    assert (checks.get_abstractrecord_type(MappingDataNode(),
                                           input_type) == type1)

    node.type.value = 'type3'
    assert checks.get_abstractrecord_type(node, input_type_no_default) == type3
    with pytest.raises(Notification) as excinfo:
        checks.get_abstractrecord_type(MappingDataNode(), input_type_no_default)
    assert excinfo.value.name == 'MissingAbstractType'

    node.type.value = 'invalid'
    with pytest.raises(Notification) as excinfo:
        checks.get_abstractrecord_type(node, input_type)
    assert excinfo.value.name == 'InvalidAbstractType'
