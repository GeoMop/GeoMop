# -*- coding: utf-8 -*-
"""
Basic rules for data validation

@author: Tomas Krizek
"""

from validation import errors


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


def check_record_key(record, key, input_type):
    """Checks a single key within a record."""
    if not isinstance(record, dict):
        raise errors.ValidationTypeError("Expecting type Record")

    # if key is not found in specifications, it is considered to be valid
    if key not in input_type['keys'] and key != 'TYPE':
        # raise UnknownKey(key, input_type['type_name']
        return True

    try:
        key_type = input_type['keys'][key]['default']['type']
    except KeyError:
        pass  # if default or type isn't specified, skip
    else:
        if key_type == 'obligatory':
            try:
                record[key]
            except KeyError:
                raise errors.MissingKey(key, input_type['type_name'])

    return True


def get_abstractrecord_type(node, input_type):
    # TODO implement for abstract records
    raise NotImplementedError
    # try:
    #     type_name = node['TYPE'].value
    # except (KeyError, TypeError):
    #     try:
    #         type_ = input_type['default_descendant']
    #     except AttributeError:
    #         raise errors.MissingAbstractRecordType()
    # else:
    #     try:
    #         type_ = input_type['implementations'][type_name]
    #     except KeyError:
    #         raise errors.InvalidAbstractRecordType(type_name,
    #                                                input_type['name'])
    #
    # return type_

