# -*- coding: utf-8 -*-
"""
Tests for validator

@author: Tomas Krizek
"""

from validation.validator import Validator
import data.data_node as dn


its_int = dict(
    base_type='Integer',
    min=0,
    max=3)

its_string = dict(
    base_type='String')

its_array = dict(
    base_type='Array',
    subtype=its_int,
    min=1,
    max=4)

its_record = dict(
    base_type='Record',
    keys={
        'a1': {'default': {'type': 'obligatory'}, 'type': its_int},
        'a2': {'default': {'type': 'obligatory'}, 'type': its_int},
        'b': {'default': {'type': 'value at declaration'},
            'type': its_int},
        'c': {'default': {'type': 'value at read time'},
            'type': its_int},
        'd': {'default': {'type': 'optional'}, 'type': its_int},
        'TYPE': {'type': its_string}},
    type_name='MyRecord')

its_record2 = dict(
    base_type='Record',
    keys={
        'b': {'default': {'type': 'obligatory'}, 'type': its_int},
        'TYPE': {'type': its_string}},
    type_name='MyRecord2')

its_abstract = dict(
    name='MyAbstractRecord',
    base_type='AbstractRecord',
    implementations={
        'record1': its_record,
        'record2': its_record2})

def test_validator():
    validator = Validator()

    # validate scalar
    node = dn.ScalarNode()
    node.value = 2
    assert validator.validate(node, its_int) is True

    node.value = 4
    assert validator.validate(node, its_int) is False
    assert len(validator.errors) == 1

    # validate record
    node = dn.CompositeNode(True)
    child1 = dn.ScalarNode()
    child1.key = dn.Key()
    child1.key.value = 'a1'
    child1.value = 1
    node.children.append(child1)
    child2 = dn.ScalarNode()
    child2.key = dn.Key()
    child2.key.value = 'a2'
    child2.value = 1
    node.children.append(child2)
    assert validator.validate(node, its_record) is True

    child3 = dn.ScalarNode()
    child3.key = dn.Key()
    child3.key.value = 'd'
    child3.value = 2
    node.children.append(child3)
    child4 = dn.ScalarNode()
    child4.key = dn.Key()
    child4.key.value = 'e'
    child4.value = 4
    node.children.append(child4)
    assert validator.validate(node, its_record) is False
    assert len(validator.errors) == 1

    # validate abstract
    # node = DataNode({'a1': 1, 'a2': 1, 'TYPE': 'record1'})
    # node.its = TestValidator.its_abstract
    # assert validator.validate(node), True)
    #
    # node.value['TYPE'].value = 'record2'
    # assert validator.validate(node), False)
    #
    # del node.value['TYPE']
    # assert validator.validate(node), False)

    # test validate
    # node = DataNode({'TYPE': 'record1', 'a1': 2, 'a2': 1})
    # node.its=TestValidator.its_abstract
    # assert validator.validate(node), True)
    #
    # node = DataNode({'TYPE': 'record2', 'b': 2})
    # node.its = TestValidator.its_abstract
    # assert validator.validate(node), True)
    #
    # node = DataNode({'TYPE': 'record1', 'a1': 5, 'a2': -1, 'e': 4, 'b': 'r'})
    # node.its = TestValidator.its_abstract
    # assert validator.validate(node), False)
    # assert len(validator.errors), 3)

    # test array
    node = dn.CompositeNode(False)
    child1 = dn.ScalarNode()
    child1.key = dn.Key()
    child1.key.value = 0
    child1.value = 0
    node.children.append(child1)
    child2 = dn.ScalarNode()
    child2.key = dn.Key()
    child2.key.value = 1
    child2.value = 1
    node.children.append(child2)
    child3 = dn.ScalarNode()
    child3.key = dn.Key()
    child3.key.value = 2
    child3.value = 1
    node.children.append(child3)
    child4 = dn.ScalarNode()
    child4.key = dn.Key()
    child4.key.value = 3
    child4.value = 2
    node.children.append(child4)
    assert validator.validate(node, its_array) is True

    child5 = dn.ScalarNode()
    child5.key = dn.Key()
    child5.key.value = 4
    child5.value = -1
    node.children.append(child5)
    child6 = dn.ScalarNode()
    child6.key = dn.Key()
    child6.key.value = 5
    child6.value = 5
    node.children.append(child6)
    assert validator.validate(node, its_array) is False
    assert len(validator.errors) == 3


if __name__ == '__main__':
    test_validator()
