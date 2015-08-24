# -*- coding: utf-8 -*-
"""
Contains format specification class and methods to parse it from JSON.

@author: Tomas Krizek
"""

from ist.formatters.json2html import HTMLFormatter
from ist.ist_formatter_module import ProfilerJSONDecoder
from ist.utils.htmltree import htmltree
import json
import os


def get_root_input_type_from_json(data):
    """Return the root input type from JSON formatted data."""
    return parse_format(json.loads(data))


class InfoTextGenerator:
    """
    Generates info_text for `DataNode`.
    Uses the Flow123d-python-utils ist library.
    """
    _input_types = {}
    RESOURCE_PATH = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], '..', 'lib', 'ist')

    @classmethod
    def init(cls, json_text):
        """Initializes the class with format information."""
        cls._input_types = {}
        node_list = json.loads(json_text, encoding="utf-8", cls=ProfilerJSONDecoder)
        for node in node_list:
            input_type_id = getattr(node, 'id', None)
            if input_type_id is not None:
                cls._input_types[input_type_id] = node

    # TODO cache html
    @classmethod
    def get_info_text(cls, input_type_id):
        """Generate an HTML documentation for the given id of `node.input_type`."""
        if input_type_id not in cls._input_types:
            return "unknown ID"

        html_content = HTMLFormatter.format([cls._input_types[input_type_id]])

        max_cols = 9

        html = htmltree('html')
        html_body = htmltree('body')

        with html_body.open('div', '', cls='container'):
            with html_body.open('div', cls='row'):
                with html_body.open('div', cls='col-md-{:d} input-reference'.format(max_cols)):
                    with html_body.open('div', cls='row'):
                        html_body.add(html_content.current())

        html_head = htmltree('head')
        html_head.style('css/main.css')
        html_head.style('css/bootstrap.min.css')
        html_head.style('css/bootstrap-toggle.min.css')
        html_head.style('css/katex.min.css')

        html_head.script('js/jquery-2.1.3.min.js')
        html_head.script('js/bootstrap.min.js')
        html_head.script('js/bootstrap-toggle.min.js')
        html_head.script('js/katex.min.js')
        html_head.script('js/main.js')

        html.add(html_head.current())
        html.add(html_body.current())
        return html.dump()


def parse_format(data):
    """Returns root input type from JSON data."""
    input_types = {}
    root_id = data[0]['id']      # set root type

    for item in data:
        input_type = _get_input_type(item)
        input_types[input_type['id']] = input_type  # register by id

    _substitute_ids_with_references(input_types)
    return input_types[root_id]


def _substitute_ids_with_references(input_types):
    """Replaces ids or type names with python object references."""
    input_type = {}

    def _substitute_implementations():
        """Replaces implementation ids with input_types."""
        impls = {}
        for id_ in input_type['implementations']:
            type_ = input_types[id_]
            impls[type_['type_name']] = type_
        input_type['implementations'] = impls

    def _substitute_default_descendant():
        """Replaces default descendant id with input_type."""
        id_ = input_type.get('default_descendant', None)
        if id_ is not None:
            input_type['default_descendant'] = input_types[id_]

    def _substitute_key_type():
        """Replaces key type with input_type."""
        # pylint: disable=unused-variable, invalid-name
        for __, value in input_type['keys'].items():
            value['type'] = input_types[value['type']]

    # pylint: disable=unused-variable, invalid-name
    for __, input_type in input_types.items():
        if input_type['base_type'] == 'Array':
            input_type['subtype'] = input_types[input_type['subtype']]
        elif input_type['base_type'] == 'AbstractRecord':
            _substitute_implementations()
            _substitute_default_descendant()
        elif input_type['base_type'] == 'Record':
            _substitute_key_type()


def _get_input_type(data):
    """Returns the input_type data structure that defines an input type
    and its constraints for validation."""
    input_type = dict(
        id=data['id'],
        base_type=data['input_type']
    )
    input_type['name'] = data.get('name', '')
    input_type['full_name'] = data.get('full_name', '')
    input_type['description'] = data.get('description', '')
    if input_type['base_type'] in ['Double', 'Integer']:
        input_type.update(_parse_range(data))
    elif input_type['base_type'] == 'Array':
        input_type.update(_parse_range(data))
        if input_type['min'] < 0:
            input_type['min'] = 0
        input_type['subtype'] = data['subtype']
    elif input_type['base_type'] == 'FileName':
        input_type['file_mode'] = data['file_mode']
    elif input_type['base_type'] == 'Selection':
        input_type['values'] = _list_to_dict(data['values'], 'name')
    elif input_type['base_type'] == 'Record':
        input_type['type_name'] = data['type_name']
        input_type['keys'] = _list_to_dict(data['keys'])
        input_type['type_full_name'] = data.get('type_full_name', '')
        input_type['implements'] = data.get('implements', [])
        input_type['reducible_to_key'] = data.get('reducible_to_key', None)
    elif input_type['base_type'] == 'AbstractRecord':
        input_type['implementations'] = data['implementations']
        input_type['default_descendant'] = data.get('default_descendant', None)
    return input_type


def _parse_range(data):
    input_type = {}
    try:
        input_type['min'] = data['range'][0]
    except (KeyError, TypeError):  # set default value
        input_type['min'] = float('-inf')
    try:
        input_type['max'] = data['range'][1]
    except (KeyError, TypeError):  # set default value
        input_type['max'] = float('inf')
    return input_type


def _list_to_dict(list_, key_label='key'):
    """
    Transforms a list of dictionaries into a dictionary of dictionaries.

    Original dictionaries are assigned key specified in each of them
    by key_label.
    """
    dict_ = {}
    for item in list_:
        dict_[item[key_label]] = item
    return dict_

