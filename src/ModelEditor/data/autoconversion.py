"""
GeoMop model auto-conversion module

Ensures auto-conversion of data for specified format.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from copy import deepcopy

from helpers import notification_handler, Notification
from util.util import TextValue

from .data_node import DataNode, MappingDataNode, SequenceDataNode
from .format import SCALAR


class AutoConverter:
    """Handle autoconverting layer of data."""

    @staticmethod
    def autoconvert(node, input_type):
        """
        Performs recursive auto-conversion on root node.

        Auto-conversions:
            1. If Array is expected and scalar/record is found, encapsulate it
               in Array(s).
            2. If Record is expected and scalar/array is found, check
               reducible_to_key. If present, create the Record.
            3. If AbstractRecord is expected and scalar/array is found, check if
               default_descendant fits rule 2.

        The function also converts data to the expected data types (if possible).
        """
        root = deepcopy(node)
        AutoConverter._autoconvert_crawl(root, input_type)
        return root

    @staticmethod
    def _autoconvert_crawl(node, input_type):
        """
        Recursively crawls through the tree structure and tries to auto-convert
        values to the expected type.
        """
        if input_type is None:
            return

        if input_type['base_type'] == 'AbstractRecord':
            try:
                it_concrete = input_type['implementations'][node.type.value]
            except (KeyError, AttributeError):
                try:
                    it_concrete = input_type['default_descendant']
                except KeyError:
                    return
            AutoConverter._autoconvert_crawl(node, it_concrete)
        elif input_type['base_type'] == 'Array':
            if node.implementation != DataNode.Implementation.sequence:
                return
            children = list(node.children)
            node.children.clear()
            for child in children:
                ac_child = AutoConverter._get_autoconverted(child, input_type['subtype'])
                node.set_child(ac_child)
                AutoConverter._autoconvert_crawl(ac_child, input_type['subtype'])
        elif input_type['base_type'] == 'Record':
            if node.implementation != DataNode.Implementation.mapping:
                return
            children = list(node.children)
            node.children.clear()
            for child in children:
                try:
                    child_it = input_type['keys'][child.key.value]['type']
                except (KeyError, AttributeError):
                    node.set_child(child)
                    continue
                else:
                    ac_child = AutoConverter._get_autoconverted(child, child_it)
                    node.set_child(ac_child)
                    AutoConverter._autoconvert_crawl(ac_child, child_it)
        elif input_type['base_type'] in SCALAR:
            ScalarConverter.convert(node, input_type)

        return

    @staticmethod
    def _get_autoconverted(node, input_type):
        """
        Auto-conversion of array and record types.

        Arrays are expanded to the expected dimension.
        Records are initialized from the reducible_to_key value.
        """
        if input_type is None:
            return node
        is_array = node.implementation == DataNode.Implementation.sequence
        is_record = node.implementation == DataNode.Implementation.mapping
        if input_type['base_type'] == 'Array' and not is_array:
            dim = AutoConverter._get_expected_array_dimension(input_type)
            return AutoConverter._expand_value_to_array(node, dim)
        elif input_type['base_type'].endswith('Record') and not is_record:
            return AutoConverter._expand_reducible_to_key(node, input_type)
        else:
            return node

    @staticmethod
    def _get_expected_array_dimension(input_type):
        """Returns the expected dimension of the input array."""
        dim = 0
        while input_type['base_type'] == 'Array':
            dim += 1
            input_type = input_type['subtype']
        return dim

    @staticmethod
    def _expand_value_to_array(node, dim):
        """Expands node value to specified dimension."""
        while dim > 0:
            array_node = SequenceDataNode(node.key, node.parent)
            array_node.span = node.span
            node.parent = array_node
            node.key = TextValue('0')
            if node.input_type is not None:
                array_node.input_type = node.input_type
                node.input_type = array_node.input_type['subtype']
            array_node.children.append(node)
            array_node.origin = DataNode.Origin.ac_array
            node = array_node
            dim -= 1
        return node

    @staticmethod
    def _expand_reducible_to_key(node, input_type):
        """Initializes a record from the reducible_to_key value."""
        if input_type is None:
            return
        try:
            key = input_type['default_descendant']['reducible_to_key']
            child_input_type = input_type['default_descendant']
        except (KeyError, TypeError):
            try:
                key = input_type['reducible_to_key']
                child_input_type = input_type
            except KeyError:
                return node

        if key is None:
            return node

        record_node = MappingDataNode(node.key, node.parent)
        record_node.span = node.span
        if hasattr(node, 'type'):
            record_node.type = node.type
            node.type = None
        node.parent = record_node
        node.origin = DataNode.Origin.ac_reducible_to_key
        node.key = TextValue(key)
        if node.input_type is not None:
            record_node.input_type = node.input_type
            node.input_type = child_input_type['keys'][key]['type']
        record_node.children.append(node)
        return record_node


class ScalarConverter:
    """Convert scalar values to their expected types."""

    @staticmethod
    def convert(node, input_type):
        """Convert value of Scalar node to expected type.

        node: :py:class:`DataNode` data structure
        input_type: definition of input_type
        """
        conversions = {
            'Bool': ScalarConverter._convert_to_bool,
            'Integer': ScalarConverter._convert_to_int,
            'Double': ScalarConverter._convert_to_float,
            'String': ScalarConverter._convert_to_string,
            'FileName': ScalarConverter._convert_to_string,
            'Selection': ScalarConverter._convert_to_string,
        }

        base_type = input_type['base_type']
        if base_type in conversions and node.value is not None:
            try:
                value = conversions[base_type](node.value)
            except ValueError:
                notification = Notification.from_name('ValueConversionError', node.value, base_type)
                notification.span = node.span
                notification_handler.report(notification)
                return
            node.value = value

    @staticmethod
    def _convert_to_bool(value):
        """Convert given value to bool."""
        if not isinstance(value, bool):
            return value.lower() in ("true", "1")
        return value

    @staticmethod
    def _convert_to_int(value):
        """Convert given value to int.

        :raises: ValueError - if the value can not be converted to integer
        """
        if not isinstance(value, int):
            return int(ScalarConverter._convert_to_float(value))
        return value

    @staticmethod
    def _convert_to_float(value):
        """Convert given value to float.

        :raises: ValueError - if the value can not be converted to float
        """
        if not isinstance(value, float):
            return float(value)
        return value

    @staticmethod
    def _convert_to_string(value):
        """Convert the given value to string."""
        if not isinstance(value, str):
            return str(value)
        return value


# initialize module
autoconvert = AutoConverter.autoconvert
