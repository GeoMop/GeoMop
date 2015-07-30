# -*- coding: utf-8 -*-
"""
Basic rules for data validation

@author: Tomas Krizek
"""

from data.validation import errors


def check_scalar(node, input_type):
    """Checks scalar node value."""
    checks = {
        'Integer': check_integer,
        'Double': check_double,
        'Bool': check_bool,
        'String': check_string,
        'Selection': check_selection,
        'FileName': check_filename
    }
    check = checks.get(input_type['base_type'], None)
    if check is None:
        raise errors.ValidationTypeError()
    return check(node.value, input_type)


def check_integer(value, input_type):
    """Checks if value is an integer within given range."""
    if not isinstance(value, int):
        raise errors.ValidationTypeError("Expecting type Integer")
    if value < input_type['min']:
        raise errors.ValueTooSmall(input_type['min'])
    if value > input_type['max']:
        raise errors.ValueTooBig(input_type['max'])
    return True


def check_double(value, input_type):
    """Checks if value is a real number within given range."""
    if not isinstance(value, (int, float)):
        raise errors.ValidationTypeError("Expecting type Double")
    if value < input_type['min']:
        raise errors.ValueTooSmall(input_type['min'])
    if value > input_type['max']:
        raise errors.ValueTooBig(input_type['max'])
    return True


# pylint: disable=unused-argument
def check_bool(value, input_type):
    """Checks if value is a boolean."""
    if not isinstance(value, bool):
        raise errors.ValidationTypeError("Expecting type Bool")
    return True


def check_string(value, input_type):
    """Checks if value is a string."""
    if not isinstance(value, str):
        raise errors.ValidationTypeError("Expecting type String")
    return True


def check_selection(value, input_type):
    """Checks if value is a valid option in given selection."""
    if value in input_type['values']:
        return True
    else:
        raise errors.InvalidOption(value, input_type['name'])


def check_filename(value, input_type):
    """Placeholder for FileName validation."""
    return check_string(value, input_type)


def check_array(value, input_type):
    """Checks if value is an array of size within a given range."""
    if not isinstance(value, (list, str)):
        raise errors.ValidationTypeError("Expecting type Array")
    if len(value) < input_type['min']:
        raise errors.NotEnoughItems(input_type['min'])
    elif len(value) > input_type['max']:
        raise errors.TooManyItems(input_type['max'])
    return True


def check_record_key(children_keys, key, input_type):
    """Checks a single key within a record."""
    # if key is not found in specifications, it is considered to be valid
    if key not in input_type['keys']:
        raise errors.UnknownKey(key, input_type['type_name'])

    try:
        key_type = input_type['keys'][key]['default']['type']
    except KeyError:
        pass  # if default or type isn't specified, skip
    else:
        if key_type == 'obligatory':
            if key not in children_keys:
                raise errors.MissingKey(key, input_type['type_name'])
    return True


def get_abstractrecord_type(node, input_type):
    """
    Returns the concrete TYPE of abstract record. ValidationErrors
    can occur if it is impossible to resolve the type.
    """
    try:
        type_node = node.type
    except AttributeError:
        raise errors.ValidationTypeError("Expected abstract record")

    if type_node is None:
        try:
            concrete_type = input_type['default_descendant']
        except KeyError:
            raise errors.MissingAbstractRecordType()
    else:
        try:
            concrete_type = input_type['implementations'][type_node.value]
        except KeyError:
            raise errors.InvalidAbstractRecordType(type_node.value,
                                                   input_type['name'])
    if concrete_type is None:
        raise errors.MissingAbstractRecordType()
    return concrete_type
