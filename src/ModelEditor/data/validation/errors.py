# -*- coding: utf-8 -*-
"""
GeoMop Model

Errors of data validation

@author: Tomas Krizek
"""


class ValidationError(Exception):
    """Error that happens during validation."""
    pass


class ValidationTypeError(ValidationError):
    """Error occurs when invalid type is encountered."""
    pass


class ValueTooSmall(ValidationError):
    """Error occurs when value is less than required minimum."""
    def __init__(self, min_value):
        message = ("Expected value larger or equal to {min_value}"
                   .format(min_value=min_value))
        super(ValueTooSmall, self).__init__(message)


class ValueTooBig(ValidationError):
    """Error occurs when value is greater than allowed maximum."""
    def __init__(self, max_value):
        message = ("Expected value smaller or equal to {max_value}"
                   .format(max_value=max_value))
        super(ValueTooBig, self).__init__(message)


class InvalidOption(ValidationError):
    """Error occurs when the selected option is not valid."""
    def __init__(self, option, selection_name):
        message = ("Option {option} does not exist in selection {selection}"
                   .format(option=option, selection=selection_name))
        super(InvalidOption, self).__init__(message)


class NotEnoughItems(ValidationError):
    """Error occurs when array does not have enough items."""
    def __init__(self, amount):
        plural = ('s' if amount > 1 else '')
        message = ("Expected at least {amount} item{s}"
                   .format(amount=amount, s=plural))
        super(NotEnoughItems, self).__init__(message)


class TooManyItems(ValidationError):
    """Error occurs when array has too many items."""
    def __init__(self, amount):
        plural = ('s' if amount > 1 else '')
        message = ("Expected at most {amount} item{s}"
                   .format(amount=amount, s=plural))
        super(TooManyItems, self).__init__(message)


class UnknownKey(ValidationError):
    """Error occurs when an unknown key is encountered in record."""
    def __init__(self, key, record_name):
        message = ("Unknown key {key} in record {record}"
                   .format(key=key, record=record_name))
        super(UnknownKey, self).__init__(message)


class MissingKey(ValidationError):
    """Error occurs when an obligatory key is not specified in record."""
    def __init__(self, key, record_name):
        message = ("Missing obligatory key {key} in record {record}"
                   .format(key=key, record=record_name))
        super(MissingKey, self).__init__(message)


class MissingAbstractRecordType(ValidationError):
    """Error occurs when AbstractRecord TYPE can't be determined."""
    def __init__(self):
        message = "Missing abstract record type"
        super(MissingAbstractRecordType, self).__init__(message)


class InvalidAbstractRecordType(ValidationError):
    """Error occurs when AbstractRecord TYPE is invalid."""
    def __init__(self, type_name, abstract_name):
        message = ("Invalid TYPE {type} for {record}"
                   .format(type=type_name, record=abstract_name))
        super(InvalidAbstractRecordType, self).__init__(message)



