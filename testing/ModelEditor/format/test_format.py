# -*- coding: utf-8 -*-
"""
Tests for format package.

@author: Tomas Krizek
"""
from format.format import parse_format, _list_to_dict


def test_root():
    data = [
      {
        "id": "cde734cca8c6d536",
        "input_type": "Bool",
      },
      {
        "id": "282546d52edd4",
        "input_type": "Bool"
      }
    ]
    root_format = parse_format(data)

    assert root_format['id'] == 'cde734cca8c6d536'


def test_optional_params():
    data = [{
      "id": "151ce92dd201d44b",
      "input_type": "",
      "name": "Integer",
      "full_name": "Integer",
      "description": "description"
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "151ce92dd201d44b"
    assert root_format['base_type'] == ""
    assert root_format['name'] == "Integer"
    assert root_format['full_name'] == "Integer"
    assert root_format['description'] == "description"

def test_integer():
    data = [{
      "id": "151ce92dd201d44b",
      "input_type": "Integer",
      "range": [
        0,
        3
      ]
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "151ce92dd201d44b"
    assert root_format['base_type'] == "Integer"
    assert root_format['min'] == 0
    assert root_format['max'] == 3

def test_double():
    data = [{
      "id": "6b1c4ede475775aa",
      "input_type": "Double",
      "range": [
        0,
        1.79769E+308
      ]
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "6b1c4ede475775aa"
    assert root_format['base_type'] == "Double"
    assert root_format['min'] == 0
    assert root_format['max'] == 1.79769e+308

def test_bool():
    data = [{
      "id": "282546d52edd4",
      "input_type": "Bool"
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "282546d52edd4"
    assert root_format['base_type'] == "Bool"

def test_string():
    data = [{
      "id": "29b5533100b6f60f",
      "input_type": "String"
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "29b5533100b6f60f"
    assert root_format['base_type'] == "String"

def test_filename():
    data = [{
      "id": "89a808b8e9515bf8",
      "input_type": "FileName",
      "file_mode": "input"
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "89a808b8e9515bf8"
    assert root_format['base_type'] == "FileName"
    assert root_format['file_mode'] == "input"

def test_selection():
    data = [{
      "id": "f9756fb2f66076a1",
      "input_type": "Selection",
      "values": [
        {
          "name": "PETSc",
          "description": "PETSc description"
        },
        {
          "name": "METIS",
          "description": "METIS description"
        }
      ]
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "f9756fb2f66076a1"
    assert root_format['base_type'] == "Selection"
    assert root_format['values']['PETSc']['description'] == "PETSc description"
    assert root_format['values']['METIS']['description'] == "METIS description"

def test_array():
    data = [{
      "id": "eee3033466b9ffa2",
      "input_type": "Array",
      "range": [
        0,
        4294967295
      ],
      "subtype": "6b1c4ede475775aa"
    }, {
        "id": "6b1c4ede475775aa",
        "input_type": "String"
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "eee3033466b9ffa2"
    assert root_format['base_type'] == "Array"
    assert root_format['min'] == 0
    assert root_format['max'] == 4294967295
    assert root_format['subtype']['base_type'] == "String"

def test_record():
    data = [{
      "id": "b9614d55a6c3462e",
      "input_type": "Record",
      "type_name": "Region",
      "type_full_name": "Region",
      "keys": [
        {
          "key": "name",
          "default": {
            "type": "obligatory",
            "value": "OBLIGATORY"
          },
          "type": "b9614d55a6c3462e"
        }
      ]
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "b9614d55a6c3462e"
    assert root_format['base_type'] == "Record"
    assert root_format['type_name'] == "Region"
    assert root_format['type_full_name'] == "Region"
    assert root_format['keys']['name']['default']['type'] == 'obligatory'
    assert root_format['keys']['name']['default']['value'] == 'OBLIGATORY'
    assert root_format['keys']['name']['type'] == root_format

def test_abstract_record():
    data = [{
      "id": "89b3f44e8ecaec1b",
      "input_type": "AbstractRecord",
      "default_descendant": "59d2b27373f5effe",
      "implementations": [
        "59d2b27373f5effe"
      ]
    }, {
        "id": "59d2b27373f5effe",
        "input_type": "Record",
        "type_name": "Descendant",
        "keys": []
    }]
    root_format = parse_format(data)

    assert root_format['id'] == "89b3f44e8ecaec1b"
    assert root_format['base_type'] == "AbstractRecord"
    assert root_format['default_descendant']['base_type'] == 'Record'
    assert "Descendant" in root_format['implementations']


def test_list_to_dict():
    data = [
      {
        "name": "PETSc",
        "description": "PETSc description"
      },
      {
        "name": "METIS",
        "description": "METIS description"
      }
    ]
    dictionary = _list_to_dict(data, 'name')

    assert dictionary['PETSc']['description'] == "PETSc description"
    assert dictionary['METIS']['description'] == "METIS description"


if __name__ == '__main__':
    test_abstract_record()
