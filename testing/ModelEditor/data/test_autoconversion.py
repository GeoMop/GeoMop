"""
Tests for auto-conversion module

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest
import data.autoconversion as ac
from data import ScalarDataNode, MappingDataNode
from util import TextValue


def test_get_expected_array_dimension():
    input_type = {
        'base_type': 'Array',
        'subtype': {
            'base_type': 'Array',
            'subtype': {
                'base_type': 'Array',
                'subtype': {'base_type': 'Integer'}
            }
        }
    }
    assert ac.AutoConverter._get_expected_array_dimension(input_type) == 3


def test_expand_value_to_array():
    node = ScalarDataNode()
    node.value = 5
    node.parent = MappingDataNode()
    node.key = TextValue()
    node.key.value = 'path'
    expanded = ac.AutoConverter._expand_value_to_array(node, 3)
    assert expanded.get_node_at_path('/path/0/0/0').value == 5


def test_expand_record():
    input_type = dict(
        base_type='Record',
        keys={
            'a': {
                'default': {'type': 'obligatory'},
                'type': dict(
                    base_type='String')}},
        type_name='MyRecord',
        reducible_to_key='a')
    root = ScalarDataNode(None, None, 'str')
    expanded = ac.AutoConverter._expand_reducible_to_key(root, input_type)
    assert expanded.get_node_at_path('/a').value == 'str'


def test_expand_abstract_record():
    input_type = dict(
        base_type='AbstractRecord',
        default_descendant=dict(
            base_type='Record',
            keys={
                'a': {
                    'default': {'type': 'obligatory'},
                    'type': dict(
                        base_type='String')}},
            type_name='MyRecord',
            reducible_to_key='a')
    )
    root = ScalarDataNode(None, None, 'str')
    root.input_type = input_type
    expanded = ac.AutoConverter._expand_reducible_to_key(root, input_type)
    assert expanded.get_node_at_path('/a').value == 'str'
    assert expanded.input_type == input_type
    assert expanded.get_node_at_path('/a').input_type['base_type'] == 'String'


def test_autoconvert():
    it_record = dict(
        base_type='Record',
        keys={
            'a': {
                'default': {'type': 'obligatory'},
                'type': dict(
                    base_type='Integer')}},
        type_name='MyRecord',
        reducible_to_key='a')
    it_array = dict(
        base_type='Array',
        subtype=dict(
            base_type='Array',
            subtype=it_record))
    input_type = dict(
        base_type='Record',
        keys={
            'path': {
                'type': it_array
            }
        },
        type_name='Root')
    root = MappingDataNode()
    node = ScalarDataNode(TextValue('path'), root, 2)
    root.children.append(node)
    converted = ac.autoconvert(root, input_type)
    assert converted.get_node_at_path('/path/0/0/a').value == 2


@pytest.mark.parametrize('base_type, data, expected', [
    ('Bool', True, True),
    ('Bool', "true", True),
    ('Bool', "false", False),
    ('Bool', "1", True),
    ('Bool', "0", False),
    ('Integer', 3, 3),
    ('Integer', True, 1),
    ('Integer', "3", 3),
    ('Integer', "3e0", 3),
    ('Integer', "3.2", 3),
    ('Integer', "3.6", 3),
    ('Double', 3.3, 3.3),
    ('Double', True, 1.0),
    ('Double', "3.2", 3.2),
    ('Double', "3.3e0", 3.3),
    ('String', 3.3, "3.3"),
    ('String', True, "True"),
    ('String', 3, "3"),
    ('Filename', 3.3, "3.3"),
    ('Filename', True, "True"),
    ('Filename', 3, "3"),
    ('Selection', 3.3, "3.3"),
    ('Selection', True, "True"),
    ('Selection', 3, "3"),
])
def test_convert_data_type(base_type, data, expected):
    input_type = dict(base_type=base_type)
    node = ScalarDataNode(value=data)
    node.span = None
    ac.ScalarConverter.convert(node, input_type)
    assert node.value == expected


def test_convert_data_type_error():
    pass


if __name__ == '__main__':
    test_autoconvert()
