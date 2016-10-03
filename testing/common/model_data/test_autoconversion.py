"""
Tests for auto-conversion module

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import os
import pytest

import model_data.autoconversion as ac
from model_data import ScalarDataNode, MappingDataNode, Validator, notification_handler
from geomop_util import TextValue

__model_data_dir__ =  os.path.dirname(os.path.realpath(__file__))
__common_dir__ =  os.path.split(__model_data_dir__)[0]

DATA_DIR = os.path.join('data', 'autoconversion')
INPUT_TYPE_FILE = os.path.join(__common_dir__, 'resources', 'ist', '00_geomop_testing_ist.json')
INPUT_TYPE_FILE183 = os.path.join(__common_dir__, 'resources', 'ist', '1.8.3.json')
INPUT_TYPE_FILE200 = os.path.join(__common_dir__, 'resources', 'ist', '2.0.0_rc.json')


@pytest.fixture(scope='module')
def loader():
    from model_data import Loader
    return Loader()


@pytest.fixture(scope='module')
def root_input_type():
    from model_data import get_root_input_type_from_json
    json_data = open(INPUT_TYPE_FILE).read()
    return get_root_input_type_from_json(json_data)


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


def _test_autoconvert():
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


def _test_transposition(loader):
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

def _report_notifications(file, notifications):
    report = "Notifications during '{0}' yaml file processing:\n".format(file)
    i = 0
    for notification in notifications:
        report += "    Not.{0}: {1}\n".format(str(i+1), str(notification))
    assert False, report

def _check_nodes(input, expected, desc):
    path = input.absolute_path
    desc_path = desc + ", path:"+ path
    
    if input.key is not None or expected.key is not None :
        if input.key is None and expected.key is not None:
            assert False,  "Input node ({0}) key  is None ({1})".format(desc_path, expected.key.value)
        elif input.key is not None and expected.key is None:
            assert False,  "Expected node ({0}) key  is None ({1})".format(desc_path, input.key.value)
        elif input.key.value != expected.key.value:
            assert False,  "Nodes ({0}) keys  is not same ({1},{2})".format(desc_path, input.key.value, expected.key.value)
    if input.type is not None or expected.type is not None :
        if input.type is None and expected.type is not None:
            assert False,  "Input node ({0}) type  is None ({1})".format(desc_path, expected.type.value)
        elif input.type is not None and expected.type is None:
            assert False,  "Expected node ({0}) type  is None ({1})".format(desc_path, input.type.value)
        elif  input.type.value != expected.type.value:
            assert False,  "Nodes types({0}) is not same ({1},{2})".format(desc_path, input.type.value, expected.type.value)
    if input.implementation != expected.implementation:
        assert False,  "Nodes types({0}) is not same ({1},{2})".format(desc_path, input.implementation, expected.implementation)
    if len(input.children) != len(expected.children):
        assert False,  "Number of nodes children ({0}) is not same ({1},{2})".format(desc_path, len(input.children), len(expected.children))
    for input_child in input.children:
        expected_child = None
        for  expected_child_test in expected.children:
            if input_child.key.value ==  expected_child_test.key.value:
                expected_child = expected_child_test
                break
        if  expected_child is None:
            assert False,  "Node child ({0}, key:{1}) is not in expected".format(desc_path, input_child.key.value)
        else:
            _check_nodes(input_child, expected_child, desc)

def test_all_files(loader):
    from model_data import get_root_input_type_from_json    
    
    DATA_DIR = os.path.join(__model_data_dir__, "autoconversion", "expected")
    RES_DIR = os.path.join(__model_data_dir__, "autoconversion", "input")
    
    files = os.listdir(path=DATA_DIR)
    for name in files:
        if name.startswith("1.8.3"):
            json_data = open(INPUT_TYPE_FILE183).read()       
        elif name.startswith("2.0.0"):
            json_data = open(INPUT_TYPE_FILE200).read()
        else:
            continue  
            
        file_expected = os.path.join(DATA_DIR, name)
        file_input = os.path.join(RES_DIR, name)
        yaml_expected = open(file_expected).read()
        yaml_input = open(file_input).read() 
        root_expected = loader.load(yaml_expected)
        root_input = loader.load(yaml_input)              
        root_input_type = get_root_input_type_from_json(json_data)
        
        notification_handler.clear()
        expected = ac.autoconvert(root_expected, root_input_type)
        validator = Validator(notification_handler)
        validator.validate(expected, root_input_type)
        not_count = len(notification_handler.notifications)
        if name.startswith("1.8.3"):
            if notification_handler.notifications[0].code == 602:
                not_count -= 1
        if  not_count != 0:
            _report_notifications(file_expected, notification_handler.notifications)
            
        notification_handler.clear()
        input = ac.autoconvert(root_input, root_input_type)
        validator = Validator(notification_handler)
        validator.validate(input, root_input_type)
        not_count = len(notification_handler.notifications)
        if name.startswith("1.8.3"):
            if notification_handler.notifications[0].code == 602:
                not_count -= 1
        if  not_count != 0:
            _report_notifications(file_input, notification_handler.notifications)
            
        _check_nodes(input, expected, "input:{0}, exp:{1}".format(file_input, file_expected)) 

if __name__ == '__main__':
    test_autoconvert()
