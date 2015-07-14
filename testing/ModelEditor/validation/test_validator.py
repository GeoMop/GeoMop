# -*- coding: utf-8 -*-
"""
Tests for validator

@author: Tomas Krizek
"""

from validation.validator import Validator
import data.data_node as dn
from data.yaml import Loader


def test_validator():
    loader = Loader()
    validator = Validator()
    
    it_int = dict(
        base_type='Integer',
        min=0,
        max=3)

    it_string = dict(
        base_type='String')
    
    it_array = dict(
        base_type='Array',
        subtype=it_int,
        min=1,
        max=4)
    
    it_record = dict(
        base_type='Record',
        keys={
            'a1': {'default': {'type': 'obligatory'}, 'type': it_int},
            'a2': {'default': {'type': 'obligatory'}, 'type': it_int},
            'b': {'default': {'type': 'value at declaration'},
                'type': it_int},
            'c': {'default': {'type': 'value at read time'},
                'type': it_int},
            'd': {'default': {'type': 'optional'}, 'type': it_int},
            'TYPE': {'type': it_string}},
        type_name='MyRecord')
    
    it_record2 = dict(
        base_type='Record',
        keys={
            'b': {'default': {'type': 'obligatory'}, 'type': it_int},
            'TYPE': {'type': it_string}},
        type_name='MyRecord2')
    
    it_abstract = dict(
        name='MyAbstractRecord',
        base_type='AbstractRecord',
        implementations={
            'record1': it_record,
            'record2': it_record2})

    # validate scalar
    node = dn.ScalarNode()
    node.value = 2
    assert validator.validate(node, it_int) is True

    node.value = 4
    assert validator.validate(node, it_int) is False
    assert len(validator.errors) == 1

    # validate record
    document = (
        "a1: 1\n"
        "a2: 1")
    node = loader.load(document)
    assert validator.validate(node, it_record) is True

    document = (
        "a1: 1\n"
        "a2: 1\n"
        "d: 2\n"
        "e: 4")
    node = loader.load(document)
    assert validator.validate(node, it_record) is False
    assert len(validator.errors) == 1

    # test array
    document = "[0, 1, 1, 2]"
    node = loader.load(document)
    assert validator.validate(node, it_array) is True

    document = "[0, 1, 1, 2, -1, 5]"
    node = loader.load(document)
    assert validator.validate(node, it_array) is False
    assert len(validator.errors) == 3

    # validate abstract
    # TODO abstract type by tag
    document = (
        "a1: 1\n"
        "a2: 1\n"
        "TYPE: record1")
    node = loader.load(document)
    assert validator.validate(node, it_abstract) is True

    node.get_child('TYPE').value = 'record2'
    assert validator.validate(node, it_abstract) is False

    document = (
        "a1: 1\n"
        "a2: 1\n")
    node = loader.load(document)
    assert validator.validate(node, it_abstract) is False

    # test validate
    document = (
        "TYPE: record1\n"
        "a1: 2\n"
        "a2: 1\n")
    node = loader.load(document)
    assert validator.validate(node, it_abstract) is True

    document = (
        "TYPE: record2\n"
        "b: 2\n")
    node = loader.load(document)
    assert validator.validate(node, it_abstract) is True

    document = (
        "TYPE: record1\n"
        "a1: 5\n"
        "a2: -1\n"
        "e: 4\n"
        "b: r")
    node = loader.load(document)
    assert validator.validate(node, it_abstract) is False
    assert len(validator.errors) == 4

if __name__ == '__main__':
    test_validator()
