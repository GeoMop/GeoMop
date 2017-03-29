"""
GeoMop model auto-conversion module

Ensures auto-conversion of data for specified format.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from copy import deepcopy

from .notifications import notification_handler, Notification
from geomop_util import TextValue, Span

from .data_node import DataNode, MappingDataNode, SequenceDataNode, ScalarDataNode
from .format import SCALAR, is_param


class AutoConverter:
    """Handle autoconverting layer of data."""
    
    in_transposition = False

    @staticmethod
    def autoconvert(node, input_type):
        """
        Performs recursive auto-conversion on root node.

        Auto-conversions:
            1. If Array is expected and scalar/record is found, either perform
               a transposition or encapsulate it in Array(s).
            2. If Record is expected and scalar/array is found, check
               reducible_to_key. If present, create the Record.
            3. If Abstract is expected and scalar/array is found, check if
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
        if input_type['base_type'] == 'Abstract':
            try:
                it_concrete = Transposer._get_it_concrete(node, input_type)
            except (KeyError, AttributeError):
                return
            AutoConverter._autoconvert_crawl(node, it_concrete)
        elif input_type['base_type'] == 'Array':
            if node.implementation != DataNode.Implementation.sequence:
                return
            if not  AutoConverter.in_transposition and Transposer._shift_array(node, input_type):
                AutoConverter._autoconvert_crawl(node, input_type)
                return
            ScalarConverter._replace_empty(node, input_type)
            children = list(node.children)
            node.children.clear()            
            for child in children:                                
                AutoConverter._autoconvert(node, child, input_type['subtype'])                
        elif input_type['base_type'] == 'Record':
            if node.implementation != DataNode.Implementation.mapping:
                return
            ScalarConverter._replace_empty(node, input_type)
            children = list(node.children)
            node.children.clear()
            for child in children:
                try:
                    child_it = input_type['keys'][child.key.value]['type']
                except (KeyError, AttributeError):
                    node.set_child(child)
                    continue
                else:
                    AutoConverter._autoconvert(node, child, child_it)
        elif input_type['base_type'] in SCALAR:
            ScalarConverter.convert(node, input_type)

        return

    @staticmethod
    def _autoconvert(node, child, input_type):
        """
        Auto-conversion of array and record types.

        Arrays are expanded to the expected dimension.
        Records are initialized from the reducible_to_key value.
        """        
        deep = True
        parent_in_transposition = AutoConverter.in_transposition
        new_node = Transposer.try_expand_reducible(child, input_type)
        if new_node is not None:
            child =  new_node
            new_node = None        
       
        if input_type is not None:
            is_array = child.implementation == DataNode.Implementation.sequence
            is_record = child.implementation == DataNode.Implementation.mapping
            if input_type['base_type'] == 'Array' and not is_array:                
                AutoConverter.in_transposition = True
                new_node = transposer.make_transposition(child, input_type, parent_in_transposition)
            elif (input_type['base_type'] in ['Record', 'Abstract']) and not is_record:
                notification = Notification.from_name("UnsupportedExpansion")
                notification.span = child.span
                notification_handler.report(notification)
                deep = False
        if new_node is not None:            
            child = new_node
        node.set_child(child)
        if deep:
            AutoConverter._autoconvert_crawl(child, input_type)
        AutoConverter.in_transposition = parent_in_transposition


class ScalarConverter:
    """Convert scalar values to their expected types."""

    @staticmethod
    def convert(node, input_type):
        """Convert value of Scalar node to expected type.

        node: :py:class:`DataNode` data structure
        input_type: definition of input_type
        """

        # do not convert parametrs
        if is_param(node.value):
            return

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
        
    @staticmethod
    def _replace_empty(node, type):
        """
        If input type is array, replace None value to empty array.
        If input type is record or abstaract, replace None value to empty record.
        """
        none = []
        for i in range(0,  len(node.children)):
            if node.children[i].value is None and \
                node.children[i].implementation == DataNode.Implementation.scalar:
                none.append(i)
        for i in none:    
            child = node.children[i]
            if type['base_type'] == 'Array':                
                input_type = type['subtype']
            else:
                if not child.key.value in type['keys']:
                    continue
                input_type = type['keys'][child.key.value]['type']
            if input_type['base_type'] == 'Array':
                array_node = SequenceDataNode(child.key, child.parent)
                array_node.span = child.span
                node.children[i] = array_node 
            elif input_type['base_type'] in ['Record', 'Abstract']:
                record_node =MappingDataNode(child.key, child.parent)
                record_node.span = child.span
                node.children[i] = record_node

class Transposer:
    """Handle the transposition autoconversion.

    This conversion happens when Array is expected, but Scalar od Record is encountered.
    Scalar values are simply encapsulated in an array of the correct dimension.

    If there is a Record, check if the sizes of all the unexpected arrays inside it
    (recursively) match. If so, proceed with the conversion. Transpose the Record into an
    Array of Records. The size of an Array is determined by the previous step. Finally,
    ensure all of the unexpected Arrays are replaced by a single value at the correct
    position.
    """

    paths_to_convert = None
    """a list of path to keys which are to be converted"""
    paths_to_dup = None
    """a list of path to keys which are to be duplicated"""
    paths_to_tagged = None
    """a list of path to keys which are to be tagged"""
    array_size = None
    """the size of the array tobe created by transposition"""
    abs_size = None
    """the size of the abstract tobe created by transposition"""
    current_path = None
    """list of keys that lead to the current node"""

    @classmethod
    def init(cls):
        """Initialize class for operation."""
        cls.paths_to_convert = []
        cls.paths_to_dup = []
        cls.paths_to_tagged = []
        cls.array_size = None
        cls.abs_size = None
        cls.current_path = ['.']

    @classmethod
    def make_transposition(cls,  node, input_type, in_transposition):
        """Transpose a record or scalar into an array."""
        # if node is scalar, convert it to array
        if node.implementation == DataNode.Implementation.scalar:
            return cls._expand_value_to_array(node)
        if len(node.children)==1 and len(node.children[0].children)==1 and \
            cls._is_dup(node, input_type):
            # automatic conversion to array with one element is fitted
            return cls._expand_value_to_array(node)
        if in_transposition:
            if not cls._shift_array(node, input_type):
                # only automatic conversion to array with one element is permited
                notification = Notification.from_name('UnsupportedTranspositionInTransposition',
                                                            input_type['base_type'])
                notification.span = node.span
                notification_handler.report(notification)
            return node        
        cls.init() 
        # verify that subtype is record
        subtype = input_type['subtype']
        
        if subtype['base_type'] != 'Record' and \
           ( subtype['base_type'] != 'Abstract' or \
              not hasattr(node, 'type') or \
              node.type.value not in input_type['subtype']['implementations']
           ):
            notification = Notification.from_name('UnsupportedTransposition',
                                                            input_type['base_type'])
            notification.span = node.span
            notification_handler.report(notification)
            return node
        assert node.implementation == DataNode.Implementation.mapping,\
            "Can not perform transposition on array"

        # get array size
        try:
            cls._get_transformation_array_size(node, subtype)
        except Notification as notification:
            notification_handler.report(notification)
            return node
        if cls.array_size is None:
            cls.array_size = 1
        cls._prepare_transformation(node, subtype)
            
        # create array
        array_node = SequenceDataNode(node.key, node.parent)
        array_node.span = node.span
        array_node.input_type = node.input_type
        array_node.origin = DataNode.Origin.ac_array
        template_node = deepcopy(node)
        template_node.parent = array_node
        template_node.input_type = subtype
        template_node.origin = DataNode.Origin.ac_transposition

        # create and transpose items of the array
        for i in range(cls.array_size):
            child_node = deepcopy(template_node)
            child_node.key = TextValue(str(i))
            # convert array to value
            for path in cls.paths_to_convert:
                node_to_convert = child_node.get_node_at_path(path)
                if i >= len(node_to_convert.children) and len(node_to_convert.children) != 1:
                    converted_node = ScalarDataNode(node_to_convert.key, node_to_convert.parent,
                                                    node_to_convert.value)
                    converted_node.span = Span(node_to_convert.span.start, node_to_convert.span.end)
                else:
                    if path in cls.paths_to_dup:
                        converted_node = node_to_convert
                    elif  len(node_to_convert.children) == 1:
                        converted_node = node_to_convert.children[0]
                    elif path in cls.paths_to_dup:
                        converted_node = node_to_convert
                    else:
                        converted_node = node_to_convert.children[i]
                    converted_node.parent = node_to_convert.parent
                    converted_node.key = node_to_convert.key
                    if converted_node.type is None or 'keys' not in subtype or \
                        converted_node.key.value not in subtype['keys']:
                        converted_node.type = node_to_convert.type
                node_to_convert.parent.set_child(converted_node)
            array_node.children.append(child_node)

        return array_node
        
    @staticmethod
    def  _shift_array(node, input_type):
        """If all children is scalar, bur is expected array, duplicate and shift it"""
        if  input_type['subtype']['base_type'] == 'Array' and \
            len(node.children)>0  and Transposer._can_shift(node, input_type):
            children = node.children
            node.children = []
            array_node = SequenceDataNode(TextValue(str(0)), node)
            array_node.span = node.span
            array_node.children = deepcopy(children)
            node.set_child(array_node)
            return True
        return False
    
    @staticmethod
    def  _can_shift(node, input_type):
        """array can be shifted"""
        for child in node.children:
            if input_type['subtype']['subtype']['base_type'] == 'Array':
                if not Transposer._can_shift(child, input_type['subtype']):
                    return False
            else:
                if child.implementation != DataNode.Implementation.scalar and \
                    input_type['subtype']['subtype']['base_type'] in SCALAR:
                    return False 
                if child.implementation == DataNode.Implementation.scalar and \
                    input_type['subtype']['subtype']['base_type'] not in SCALAR:
                    return False          
        return True
    
    @staticmethod
    def  _is_dup(node, input_type):
        """array with duplicate length"""
        for child in node.children:
            if input_type['subtype']['base_type'] == 'Array':
                return True
            else:
                if child.implementation != DataNode.Implementation.scalar and \
                    input_type['subtype']['base_type'] in SCALAR:
                    return False 
                if child.implementation == DataNode.Implementation.scalar and \
                    input_type['subtype']['base_type'] not in SCALAR:
                    return False          
        return True

    @classmethod
    def _get_transformation_array_size(cls, node, input_type, deep=False):
        """Return transformation array size."""
        if  input_type['base_type'] == 'Abstract' and \
            node.implementation != DataNode.Implementation.sequence: 
            for child in node.children:
#                try:
#                    it_concrete = cls._get_it_concrete(node, input_type)
#                    item_type = it_concrete['keys'][child.key.value]['type']
#                except (KeyError, AttributeError):
#                    pass
                if len(child.children)==0 and \
                    child.implementation == DataNode.Implementation.scalar:
                    if cls.abs_size is None:                        
                        cls.abs_size = 1                    
                elif len(child.children) == 1:
                    if cls.abs_size is None:                        
                        cls.abs_size = 1
                elif cls.abs_size is None or cls.abs_size == 1:
                    cls.abs_size = len(child.children)
                elif cls.abs_size != len(child.children):                    
                    notification = Notification.from_name(
                        "DifferentArrayLengthForTransposition")
                    notification.span = node.span
                    raise notification
            if cls.abs_size is None:
                cls.abs_size = 0                
        else:
                        
            # find a children node that has an array instead of record or scalar
            for i in range(0, len(node.children)):                
                child = node.children[i]              
                # the key is not specified in input type
                if 'keys' not in input_type or child.key.value not in input_type['keys']:
                    continue
                else:
                    child_type = input_type['keys'][child.key.value]['type']
                    
                if child.implementation == DataNode.Implementation.sequence and \
                    child_type['base_type'] == 'Abstract':
                    new_node = Transposer.try_expand_reducible(child, child_type)
                    if new_node is not None:
                        node.children[i] = new_node
                        child = new_node

                if child.implementation == DataNode.Implementation.sequence:                    
                    if child_type['base_type'] == 'Record':
                        notification = Notification.from_name("InvalidTransposition")
                        notification.span = child.span
                        raise notification
                    elif child_type['base_type'] != 'Array':                         
                        if cls.array_size is None:
                            cls.array_size = len(child.children)
                        elif cls.array_size == len(child.children) or len(child.children) == 1:
                            pass
                        else:    
                            notification = Notification.from_name(
                                "DifferentArrayLengthForTransposition")
                            notification.span = child.span
                            raise notification
                    elif cls._is_dup(child, child_type):
                        if cls.array_size is None:
                            cls.array_size = 1                            
                elif child.implementation == DataNode.Implementation.scalar:                    
                    if cls.array_size is None:
                        cls.array_size = 1
                else:
                    # verify array size recursively
                    if len(child.children)>0:
                        cls.current_path.append(child.key.value)
                        cls._get_transformation_array_size(child, child_type, True)
                        cls.current_path.pop()
                    else:    
                            notification = Notification.from_name(
                                "InvalidTransposition")
                            notification.span = child.span
                            raise notification
        return cls.array_size

    @classmethod
    def _prepare_transformation(cls, node, input_type):
        """Return transformation array size."""
        if cls.abs_size is not None and \
            (cls.array_size is None or cls.array_size==1):
            cls.array_size = cls.abs_size
        if  input_type['base_type'] == 'Abstract' and \
            node.implementation != DataNode.Implementation.sequence:
            for child in node.children: 
                try:
                    item_type = None
                    it_concrete = cls._get_it_concrete(node, input_type)
                    item_type = it_concrete['keys'][child.key.value]['type']                  
                except (KeyError, AttributeError):
                    pass
                if len(child.children)==0 and \
                    child.implementation == DataNode.Implementation.scalar:                    
                    cls.paths_to_dup.append('/'.join(cls.current_path + [child.key.value]))
                    cls.paths_to_convert.append('/'.join(cls.current_path + [child.key.value]))
                elif len(child.children)==1:
                    cls.paths_to_dup.append('/'.join(cls.current_path + [child.key.value]))
                    cls.paths_to_convert.append('/'.join(cls.current_path + [child.key.value]))
                elif len(child.children)==cls.array_size:
                    cls.paths_to_convert.append('/'.join(cls.current_path + [child.key.value]))
                else:
                    if item_type is not None and \
                        item_type['base_type'] == 'Array' and cls._is_dup(child, item_type):
                        cls.paths_to_dup.append('/'.join(cls.current_path + [child.key.value]))
                        cls.paths_to_convert.append('/'.join(cls.current_path + [child.key.value]))
                    else:
                        notification = Notification.from_name("InvalidAbstractTranspositionLen")
                        notification.span = child.span
                        notification_handler.report(notification)
        else:
            # find a children node that has an array instead of record or scalar
            for child in node.children:                
                # the key is not specified in input type
                if 'keys' not in input_type or child.key.value not in input_type['keys']:
                    continue
                else:
                    child_type = input_type['keys'][child.key.value]['type']

                if child.implementation == DataNode.Implementation.sequence or \
                    child.implementation == DataNode.Implementation.scalar:
                    if child_type['base_type'] == 'Array' and \
                        cls._is_dup(child, child_type):
                        cls.paths_to_dup.append('/'.join(cls.current_path + [child.key.value]))    
                    cls.paths_to_convert.append('/'.join(cls.current_path + [child.key.value]))
                else:
                    cls.current_path.append(child.key.value)
                    cls._prepare_transformation(child, child_type)
                    cls.current_path.pop()
        return cls.array_size
        
    @staticmethod
    def _get_it_concrete(node, input_type):
        """return concrete it"""
        try:
            it_concrete = input_type['implementations'][node.type.value]
        except (KeyError, AttributeError):
            it_concrete = input_type['default_descendant']
        return it_concrete

    @staticmethod
    def _expand_value_to_array(node, value=None):
        """Expands node value to an array."""
        array_node = SequenceDataNode(node.key, node.parent)
        array_node.span = node.span
        node.parent = array_node
        node.key = TextValue('0')
        if node.input_type is not None:
            array_node.input_type = node.input_type
            node.input_type = array_node.input_type['subtype']
        if value is None:
            array_node.children.append(node)
        else:
            array_node.children.append(value)
        array_node.origin = DataNode.Origin.ac_array
        return array_node
        
    @staticmethod
    def try_expand_reducible(node, input_type):
        """Initializes a record from the reducible_to_key value."""
        if input_type is None or \
            not (input_type['base_type'] in ['Record', 'Abstract']) or \
            node.implementation == DataNode.Implementation.mapping:
            return None
        
        if input_type['base_type'] == 'Record':
            child_type = input_type
        else:
            try:
                child_type = Transposer._get_it_concrete(node, input_type)            
            except (KeyError, AttributeError):
                return None
        
        if  child_type is None or 'reducible_to_key' not in child_type:
            return None
        
        key = child_type['reducible_to_key']

        if key is None:
            return None

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
            node.input_type = child_type['keys'][key]['type']
        record_node.children.append(node)        
        return record_node

# initialize module
autoconvert = AutoConverter.autoconvert
transposer = Transposer()

__all__ = ['autoconvert', 'AutoConverter']
