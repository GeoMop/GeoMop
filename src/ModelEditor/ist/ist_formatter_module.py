# encoding: utf-8
# author:   Jan Hybs
import json

from .utils.htmltree import htmltree


class InfoTextGenerator:
    """
    Generates info_text for `DataNode`.
    """
    _input_types = {}

    @classmethod
    def init(cls, json_text):
        """Initializes the class with format information."""
        data = json.loads(json_text, encoding="utf-8")
        for item in data:
            if 'id' in item:
                cls._input_types[item['id']] = item

    @classmethod
    def get_info_text(cls, record_id, selected_key=None, abstract_id=None, selected_item=None):
        """Generates HTML documentation for `record_id` with `selected_key`.

        The first key is selected by default. If `abstract_id` is specified, a documentation for
        a parent abstract record is generated. If the selected key type is of type `Selection`,
        then `selected_item` will be selected."""
        if record_id not in cls._input_types:
            return "unknown record_id"

        html = htmltree('html')
        html_body = htmltree('body')

        with html_body.open('div', cls='container-fluid fill'):
            if abstract_id in cls._input_types:
                html_body.add(cls._generate_abstract(abstract_id))
            html_body.add(cls._generate_record(record_id, selected_key, selected_item))

        html_head = htmltree('head')
        html_head.style('bootstrap.min.css')
        html_head.style('katex.min.css')
        html_head.style('main.css')
        html_head.script('jquery-2.1.3.min.js')
        html_head.script('bootstrap.min.js')

        html_body.script('katex.min.js')
        html_body.script('main.js')

        html.add(html_head.current())
        html.add(html_body.current())
        return r'<!DOCTYPE html>' + html.dump()

    @classmethod
    def _generate_abstract(cls, abstract_id):
        """Generates documentation for top-level abstract record."""
        pass

    @classmethod
    def _generate_record(cls, record_id, selected_key=None, selected_item=None):
        """Generates documentation for record."""
        section = htmltree('section', cls='row record')
        type_ = cls._input_types[record_id]

        with section.open('header'):
            section.tag('h2', type_['type_name'])
            section.tag('p', type_['description'], cls='description')

        with section.open('div', cls='key-list col-md-4 col-sm-4 col-xs-4'):
            with section.open('div', cls='item-list'):
                if 'keys' in type_:
                    if selected_key is None and len(type_['keys']) > 0:
                        selected_key = type_['keys'][0]['key']
                    for key in type_['keys']:
                        if key['key'] == selected_key:
                            selected_key_type = key
                            cls_ = 'selected'
                        else:
                            cls_ = ''
                        section.tag('a', key['key'], cls=cls_)

        with section.open('div', cls='key-description col-md-4 col-sm-4 col-xs-4'):
            with section.open('header'):
                section.tag('h3', selected_key)
                if 'default' in selected_key_type and 'value' in selected_key_type['default']:
                    with section.open('div', cls='small'):
                        section.tag('span', 'Default value: ', cls='leading-text')
                        section.tag('span', selected_key_type['default']['value'],
                                    cls='chevron skew')
            if 'description' in selected_key_type:
                section.tag('p', selected_key_type['description'], cls='description')

        key_type = cls._input_types.get(selected_key_type['type'])
        if key_type is not None and 'input_type' in key_type:
            cls_ = 'key-type col-md-4 col-sm-4 col-xs-4 '
            if key_type['input_type'] == 'Record':
                cls_ += 'record'
            elif key_type['input_type'] == 'AbstractRecord':
                cls_ += 'abstract'
            else:
                cls_ += 'scalar'
                section.add(cls._generate_key_type_scalar(key_type, selected_item, cls_=cls_))

        return section.current()

    @classmethod
    def _generate_key_type_scalar(cls, key_type, selected_item=None, cls_=''):
        """Generates documentation for scalar key type."""
        div = htmltree('div', cls=cls_)
        with div.open('header'):
            div.tag('h2', key_type['name'])
            if key_type['input_type'] in ['Integer', 'Double']:
                range = NumberRange(key_type)
                div.tag('span', str(range), cls='small')
        return div.current()


class NumberRange:
    """
    Class representing simple number range
    """

    def __init__(self, input_type):
        self.min = self.max = ''
        if 'range' in input_type:
                self.min = input_type['range'][0]
                self.max = input_type['range'][1]

    replacements = {
        '2147483647': 'INT32 MAX',
        '4294967295': 'UINT32 MAX',
        '-2147483647': 'INT32 MIN',
        '1.79769e+308': '+inf',
        '-1.79769e+308': '-inf',
        '': 'unknown range'
    }

    def _format(self):
        """
        Method will will return string representation of this instance
        :return:
        """
        min_value = self.replacements.get(str(self.min), str(self.min))
        max_value = self.replacements.get(str(self.max), str(self.max))
        l_brace = '(' if min_value.find('inf') != -1 else '['
        r_brace = ')' if max_value.find('inf') != -1 else ']'

        return '{l_brace}{min_value}, {max_value}{r_brace}'.format(
            l_brace=l_brace, r_brace=r_brace,
            min_value=min_value, max_value=max_value)

    def __repr__(self):
        """Returns string representation."""
        return self._format()

