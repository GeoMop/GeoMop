# -*- coding: utf-8 -*-
"""
GeoMop Model

Tests for basic validation checks.

@author: Tomas Krizek
"""

import pytest

from data.validation import errors, checks
import data.data_node as dn


def test_check_integer():
    input_type = dict(min=0, max=3)
    input_type_inf = dict(min=float('-inf'), max=float('inf'))

    assert checks.check_integer(3, input_type_inf) is True
    assert checks.check_integer(-2, input_type_inf) is True

    with pytest.raises(errors.ValidationTypeError):
        checks.check_integer(2.5, input_type)
        checks.check_integer("3", input_type)
        checks.check_integer({}, input_type)
        checks.check_integer([], input_type)

    assert checks.check_integer(3, input_type) is True
    assert checks.check_integer(2, input_type) is True
    assert checks.check_integer(0, input_type) is True

    with pytest.raises(errors.ValueTooSmall):
        checks.check_integer(-1, input_type)

    with pytest.raises(errors.ValueTooBig):
        checks.check_integer(5, input_type)


def test_check_double():
    input_type = dict(min=0, max=3.14)
    input_type_inf = dict(min=float('-inf'), max=float('inf'))

    assert checks.check_double(3.14, input_type_inf) is True
    assert checks.check_double(-2, input_type_inf) is True  # accepts int

    with pytest.raises(errors.ValidationTypeError):
        checks.check_double("3.14", input_type)
        checks.check_double({}, input_type)
        checks.check_double([], input_type)

    assert checks.check_double(3.14, input_type) is True
    assert checks.check_double(2.5, input_type) is True
    assert checks.check_double(0, input_type) is True

    with pytest.raises(errors.ValueTooSmall):
        checks.check_double(-1.3, input_type)

    with pytest.raises(errors.ValueTooBig):
        checks.check_double(5, input_type)


def test_check_bool():
    input_type = dict()
    assert checks.check_bool(True, input_type) is True
    assert checks.check_bool(False, input_type) is True

    with pytest.raises(errors.ValidationTypeError):
        checks.check_bool(0, input_type)
        checks.check_bool(1, input_type)
        checks.check_bool("1", input_type)
        checks.check_bool("false", input_type)
        checks.check_bool({}, input_type)
        checks.check_bool([], input_type)


def test_check_string():
    input_type = dict()
    assert checks.check_string("abc", input_type) is True

    with pytest.raises(errors.ValidationTypeError):
        checks.check_string(0, input_type)
        checks.check_string({}, input_type)
        checks.check_string([], input_type)


def test_check_selection():
    input_type = dict(values={'a': 1, 'b': 2, 'c': 3}, name="MySelection")

    assert checks.check_selection('a', input_type) is True
    assert checks.check_selection('b', input_type) is True
    assert checks.check_selection('c', input_type) is True

    with pytest.raises(errors.InvalidOption):
        assert checks.check_selection('d', input_type)


def test_check_filename():
    input_type = dict()
    assert checks.check_filename("abc", input_type) is True

    with pytest.raises(errors.ValidationTypeError):
        checks.check_filename(0, input_type)
        checks.check_filename({}, input_type)
        checks.check_filename([], input_type)


def test_check_array():
    input_type = dict(min=1, max=5)
    input_type_inf = dict(min=0, max=float('inf'))
    assert checks.check_array([], input_type_inf) is True
    assert checks.check_array([None]*2, input_type) is True
    assert checks.check_array([None]*1, input_type) is True
    assert checks.check_array([None]*5, input_type) is True

    with pytest.raises(errors.ValidationTypeError):
        checks.check_array(None, input_type)

    with pytest.raises(errors.NotEnoughItems):
        checks.check_array([], input_type)

    with pytest.raises(errors.TooManyItems):
        checks.check_array([None]*6, input_type)


def test_check_record_key():
    keys = {
        'a1': {'default': {'type': 'obligatory'}},
        'a2': {'default': {'type': 'obligatory'}},
        'b': {'default': {'type': 'value at declaration'}},
        'c': {'default': {'type': 'value at read time'}},
        'd': {'default': {'type': 'optional'}}
    }
    input_type = dict(keys=keys, type_name='MyRecord')

    assert checks.check_record_key(['a1'], 'a1', input_type) is True
    assert checks.check_record_key(['a1'], 'b', input_type) is True
    assert checks.check_record_key(['a1'], 'c', input_type) is True
    assert checks.check_record_key(['a1'], 'd', input_type) is True

    with pytest.raises(errors.UnknownKey):
        checks.check_record_key('unknown', 'unknown', input_type)

    with pytest.raises(errors.MissingKey):
        checks.check_record_key(['a1'], 'a2', input_type)


def test_check_abstractrecord():
    type1 = dict(type_name='type1')
    type2 = dict(type_name='type2')
    type3 = dict(type_name='type3')
    input_type = dict(default_descendant=type1, implementations={
        'type1': type1, 'type2': type2, 'type3': type3}, name='MyAbstractRecord')
    input_type_no_default = dict(implementations={'type1': type1,
                                                  'type2': type2,
                                                  'type3': type3})
    node = dn.CompositeNode(True)
    type_node = dn.ScalarNode()
    type_node.key = dn.TextValue()
    type_node.key.value = 'TYPE'
    type_node.value = 'type2'
    node.children.append(type_node)

    assert checks.get_abstractrecord_type(node, input_type) == type2
    assert (checks.get_abstractrecord_type(dn.CompositeNode(True),
                                           input_type) == type1)

    type_node.value = 'type3'
    assert checks.get_abstractrecord_type(node, input_type_no_default) == type3
    with pytest.raises(errors.MissingAbstractRecordType):
        checks.get_abstractrecord_type(dn.CompositeNode(True), input_type_no_default)

    type_node.value = 'invalid'
    with pytest.raises(errors.InvalidAbstractRecordType):
        checks.get_abstractrecord_type(node, input_type)
