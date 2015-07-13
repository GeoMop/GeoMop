# -*- coding: utf-8 -*-
"""
GeoMop Model

Errors of data validation

@author: Tomas Krizek
"""


class ValidationError(Exception):
    pass


class ValidationTypeError(ValidationError):
    pass


class ValueTooSmall(ValidationError):
    def __init__(self, min_value):
        message = "Expected value larger or equal to {min_value}".format(min_value=min_value)
        super(ValueTooSmall, self).__init__(message)


class ValueTooBig(ValidationError):
    def __init__(self, max_value):
        message = "Expected value smaller or equal to {max_value}".format(max_value=max_value)
        super(ValueTooBig, self).__init__(message)


class InvalidOption(ValidationError):
    def __init__(self, option, selection_name):
        message = "Option {option} does not exist in selection {selection}".format(option=option, selection=selection_name)
        super(InvalidOption, self).__init__(message)


class NotEnoughItems(ValidationError):
    def __init__(self, amount):
        plural = ('s' if amount > 1 else '')
        message = "Expected at least {amount} item{s}".format(amount=amount, s=plural)
        super(NotEnoughItems, self).__init__(message)


class TooManyItems(ValidationError):
    def __init__(self, amount):
        plural = ('s' if amount > 1 else '')
        message = "Expected at most {amount} item{s}".format(amount=amount, s=plural)
        super(TooManyItems, self).__init__(message)


class UnknownKey(ValidationError):
    def __init__(self, key, record_name):
        message = "Unknown key {key} in record {record}".format(key=key, record=record_name)
        super(UnknownKey, self).__init__(message)


class MissingKey(ValidationError):
    def __init__(self, key, record_name):
        message = "Missing obligatory key {key} in record {record}".format(key=key, record=record_name)
        super(MissingKey, self).__init__(message)


class MissingAbstractRecordType(ValidationError):
    def __init__(self):
        message = "Missing abstract record type"
        super(MissingAbstractRecordType, self).__init__(message)


class InvalidAbstractRecordType(ValidationError):
    def __init__(self, type_name, abstract_name):
        message = "Invalid TYPE {type} for {record}".format(type=type_name, record=abstract_name)
        super(InvalidAbstractRecordType, self).__init__(message)



