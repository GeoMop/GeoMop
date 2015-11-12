"""
Tests for auto-conversion module

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

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
    assert ac._get_expected_array_dimension(input_type) == 3


def test_expand_value_to_array():
    node = ScalarDataNode()
    node.value = 5
    node.parent = MappingDataNode()
    node.key = TextValue()
    node.key.value = 'path'
    expanded = ac._expand_value_to_array(node, 3)
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
    expanded = ac._expand_reducible_to_key(root, input_type)
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
    expanded = ac._expand_reducible_to_key(root, input_type)
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

if __name__ == '__main__':
    test_autoconvert()
