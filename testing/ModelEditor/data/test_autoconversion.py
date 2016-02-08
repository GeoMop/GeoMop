"""
Tests for auto-conversion module

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import os
import pytest
import data.autoconversion as ac
from data import ScalarDataNode, MappingDataNode
from helpers import notification_handler
from util import TextValue

DATA_DIR = os.path.join('data', 'autoconversion')
INPUT_TYPE_FILE = os.path.join('resources', 'format', '00_geomop_testing_ist.json')


@pytest.fixture(scope='module')
def loader():
    from data import Loader
    return Loader()


@pytest.fixture(scope='module')
def root_input_type():
    from data import get_root_input_type_from_json
    json_data = open(INPUT_TYPE_FILE).read()
    return get_root_input_type_from_json(json_data)


# def test_get_expected_array_dimension():
#     input_type = {
#         'base_type': 'Array',
#         'subtype': {
#             'base_type': 'Array',
#             'subtype': {
#                 'base_type': 'Array',
#                 'subtype': {'base_type': 'Integer'}
#             }
#         }
#     }
#     assert ac.AutoConverter._get_expected_array_dimension(input_type) == 3


def test_expand_value_to_array():
    node = ScalarDataNode()
    node.value = 5
    node.parent = MappingDataNode()
    node.key = TextValue()
    node.key.value = 'path'
    node = ac.transposer._expand_value_to_array(node)
    node = ac.transposer._expand_value_to_array(node)
    node = ac.transposer._expand_value_to_array(node)
    assert node.get_node_at_path('/path/0/0/0').value == 5


def test_expand_record():
    input_type = dict(
        base_type='Record',
        keys={
            'a': {
                'default': {'type': 'obligatory'},
                'type': dict(
                    base_type='String')}},
        name='MyRecord',
        reducible_to_key='a')
    root = ScalarDataNode(None, None, 'str')
    expanded = ac.AutoConverter._expand_reducible_to_key(root, input_type)
    assert expanded.get_node_at_path('/a').value == 'str'


def test_expand_abstract_record():
    input_type = dict(
        base_type='Abstract',
        default_descendant=dict(
            base_type='Record',
            keys={
                'a': {
                    'default': {'type': 'obligatory'},
                    'type': dict(
                        base_type='String')}},
            name='MyRecord',
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
        name='MyRecord',
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
        name='Root')
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
    ('FileName', 3.3, "3.3"),
    ('FileName', True, "True"),
    ('FileName', 3, "3"),
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


def test_transposition(loader):
    root_input_type = dict(
        name='RootTransposeRec',
        base_type='Record',
        keys=dict(
            set=dict(type=dict(
                base_type='Array',
                min=1,
                max=4,
                subtype=dict(
                    name='TransposeSubRec1',
                    base_type='Record',
                    keys=dict(
                        one=dict(type=dict(
                            base_type='Integer'
                        )),
                        two=dict(type=dict(
                            base_type='Array',
                            min=1,
                            max=10,
                            subtype=dict(
                                base_type='Integer'
                            )
                        )),
                        three=dict(type=dict(
                            name='TransposeSubRec2',
                            base_type='Record',
                            keys=dict(
                                key_a=dict(type=dict(
                                    base_type='String'
                                )),
                                key_b=dict(type=dict(
                                    base_type='Bool'
                                )),
                            )
                        )),
                        four=dict(type=dict(
                            base_type='Double'
                        )),
                        five=dict(type=dict(
                            base_type='Selection',
                            values=dict(
                                one=None,
                                two=None,
                                ten=None
                            )
                        ))
                    )
                )
            )),
            default=dict(type=dict(
                base_type='Bool'
            ))
        )
    )

    data = (
        "set:\n"
        "  one: [1,2,3]\n"
        "  two: [2,3]\n"
        "  three:\n"
        "    key_a: [A, B, C]\n"
        "    key_b: [false,true,false]\n"
        "  four: [1.5, 2.5, 3.5]\n"
        "  five: [one, two, ten]\n"
        "default: true\n"
    )
    root = loader.load(data)
    root = ac.autoconvert(root, root_input_type)
    assert len(root.children[0].children) == 3
    assert root.children[1].value is True
    node = root.children[0].children[0]
    assert len(node.children) == 5
    assert node.children[0].value == 1
    assert len(node.children[1].children) == 2
    assert len(node.children[2].children) == 2
    assert node.children[2].children[0].value == 'A'
    assert node.children[2].children[1].value is False
    assert node.children[3].value == 1.5
    assert node.children[4].value == 'one'
    node = root.children[0].children[1]
    assert len(node.children) == 5
    assert node.children[0].value == 2
    assert node.children[2].children[0].value == 'B'
    assert node.children[2].children[1].value is True
    assert node.children[3].value == 2.5
    assert node.children[4].value == 'two'
    node = root.children[0].children[2]
    assert len(node.children) == 5
    assert node.children[0].value == 3
    assert node.children[2].children[0].value == 'C'
    assert node.children[2].children[1].value is False
    assert node.children[3].value == 3.5
    assert node.children[4].value == 'ten'

    data = (
        "set:\n"
        "  one: 1\n"
        "  two: [2,3]\n"
        "  three:\n"
        "    key_a: A\n"
        "    key_b: false\n"
        "  four: 1.5\n"
        "  five: one\n"
        "default: true\n"
    )
    root = loader.load(data)
    root = ac.autoconvert(root, root_input_type)
    assert len(root.children[0].children) == 1
    assert root.children[1].value is True
    node = root.children[0].children[0]
    assert len(node.children) == 5
    assert node.children[0].value == 1
    assert len(node.children[1].children) == 2
    assert len(node.children[2].children) == 2
    assert node.children[2].children[0].value == 'A'
    assert node.children[2].children[1].value is False
    assert node.children[3].value == 1.5
    assert node.children[4].value == 'one'

    data = (
        "set:\n"
        "  one: []\n"
        "  two: [2,3]\n"
        "  three:\n"
        "    key_a: [A, B, C]\n"
        "    key_b: false\n"
        "  four: [1.5, 2.5, 3.5]\n"
        "  five: one\n"
        "default: true\n"
    )
    root = loader.load(data)
    notification_handler.clear()
    root = ac.autoconvert(root, root_input_type)
    assert len(notification_handler.notifications) == 1
    assert notification_handler.notifications[0].name == 'DifferentArrayLengthForTransposition'

    data = (
        "set:\n"
        "  one: [1, 2, 3]\n"
        "  two: [2,3]\n"
        "  three:\n"
        "    key_a: [A, B]\n"
        "    key_b: false\n"
        "  four: [1.5, 2.5, 3.5]\n"
        "  five: one\n"
        "default: true\n"
    )
    root = loader.load(data)
    notification_handler.clear()
    root = ac.autoconvert(root, root_input_type)
    assert len(notification_handler.notifications) == 1
    assert notification_handler.notifications[0].name == 'DifferentArrayLengthForTransposition'

    data = (
        "set:\n"
        "  one: [1, 2]\n"
        "  two: [2,3]\n"
        "  three:\n"
        "    - key_a: A\n"
        "      key_b: false\n"
        "    - key_a: B\n"
        "      key_b: false\n"
        "  four: 1.5\n"
        "  five: one\n"
        "default: true\n"
    )
    root = loader.load(data)
    notification_handler.clear()
    root = ac.autoconvert(root, root_input_type)
    assert len(notification_handler.notifications) == 1
    assert notification_handler.notifications[0].name == 'InvalidTransposition'


if __name__ == '__main__':
    test_autoconvert()
