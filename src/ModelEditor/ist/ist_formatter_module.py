# encoding: utf-8
# author:   Jan Hybs
import json

from ist.formatters.json2html import get_info_text
from ist.nodes import TypedList


class InfoTextGenerator:
    """
    Generates info_text for `DataNode`.
    """
    _input_types = {}

    @classmethod
    def init(cls, json_text):
        """Initializes the class with format information."""
        cls._input_types = {}
        node_list = json.loads(json_text, encoding="utf-8", cls=ProfilerJSONDecoder)
        for node in node_list:
            input_type_id = getattr(node, 'id', None)
            if input_type_id is not None:
                cls._input_types[input_type_id] = node

    @classmethod
    def get_info_text(cls, input_type, **kwargs):
        """Generate an HTML documentation for the given id of `node.input_type`."""
        if input_type is None:
            return "unknown input_type"
        input_type_id = input_type['id']
        if input_type_id not in cls._input_types:
            return "unknown ID"
        input_type = cls._input_types[input_type_id]
        return get_info_text(input_type, **kwargs)


class ProfilerJSONDecoder(json.JSONDecoder):
    def decode(self, json_string):
        default_obj = super(ProfilerJSONDecoder, self).decode(json_string)
        lst = TypedList()
        lst.parse(default_obj)
        return lst
