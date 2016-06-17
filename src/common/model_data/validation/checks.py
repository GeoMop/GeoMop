"""Basic rules for data validation

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
# pylint: disable=unused-argument

from ..data_node import DataNode
from ..notifications import Notification


def check_scalar(node, input_type):
    """Checks scalar node value."""
    if node.implementation != DataNode.Implementation.scalar:
        raise Notification.from_name('ValidationTypeError', 'Scalar')
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
        raise Notification.from_name('ValidationTypeError', 'Scalar')
    return check(node.value, input_type)


def check_integer(value, input_type):
    """Checks if value is an integer within given range."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise Notification.from_name('ValidationTypeError', 'Integer')
    if value < input_type['min']:
        raise Notification.from_name('ValueTooSmall', input_type['min'])
    if value > input_type['max']:
        raise Notification.from_name('ValueTooBig', input_type['max'])
    return True


def check_double(value, input_type):
    """Checks if value is a real number within given range."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise Notification.from_name('ValidationTypeError', 'Double')
    if value < input_type['min']:
        raise Notification.from_name('ValueTooSmall', input_type['min'])
    if value > input_type['max']:
        raise Notification.from_name('ValueTooBig', input_type['max'])
    return True


def check_bool(value, input_type):
    """Checks if value is a boolean."""
    if not isinstance(value, bool):
        raise Notification.from_name('ValidationTypeError', 'Bool')
    return True


def check_string(value, input_type):
    """Checks if value is a string."""
    if not isinstance(value, str):
        raise Notification.from_name('ValidationTypeError', 'String')
    return True


def check_selection(value, input_type):
    """Checks if value is a valid option in given selection."""
    if value in input_type['values']:
        return True
    else:
        raise Notification.from_name('InvalidSelectionOption', input_type['name'], value)


def check_filename(value, input_type):
    """Placeholder for FileName validation."""
    return check_string(value, input_type)


def check_array(value, input_type):
    """Checks if value is an array of size within a given range."""
    if not isinstance(value, (list, str)):
        raise Notification.from_name('ValidationTypeError', 'Array')
    if len(value) < input_type['min']:
        raise Notification.from_name('NotEnoughItems', input_type['min'], input_type['max'])
    elif len(value) > input_type['max']:
        raise Notification.from_name('TooManyItems', input_type['min'], input_type['max'])
    return True


def check_record_key(children_keys, key, input_type):
    """Checks a single key within a record."""
    # if key is not found in specifications, it is considered to be valid
    if key not in input_type['keys']:
        if key == 'fatal_error':
            raise Notification.from_name('SilencedNotification')
        raise Notification.from_name('UnknownRecordKey', key, input_type['name'])

    try:
        key_type = input_type['keys'][key]['default']['type']
    except KeyError:
        pass  # if default or type isn't specified, skip
    else:
        if key_type == 'obligatory':
            if key not in children_keys:
                raise Notification.from_name('MissingObligatoryKey', key,
                                                 input_type['name'])
    return True


def get_abstractrecord_type(node, input_type):
    """
    Returns the concrete TYPE of abstract record. ValidationErrors
    can occur if it is impossible to resolve the type.
    """
    try:
        type_node = node.type
    except AttributeError:
        raise Notification.from_name('ValidationTypeError', 'Abstract')

    if type_node is None:
        try:
            concrete_type = input_type['default_descendant']
        except KeyError:
            raise Notification.from_name('MissingAbstractType')
    else:
        try:
            concrete_type = input_type['implementations'][type_node.value]
        except KeyError:
            raise Notification.from_name('InvalidAbstractType', type_node.value,
                                             input_type['name'])
    if concrete_type is None:
        raise Notification.from_name('MissingAbstractType')
    return concrete_type
