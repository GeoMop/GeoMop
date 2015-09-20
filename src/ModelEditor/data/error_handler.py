"""
Error Handler module for capturing and reporting errors
that occur when processing the data structure.
"""

__author__ = 'Tomas Krizek'

import data.data_node as dn
from data.validation import errors


class ErrorHandler:
    """
    Handles errors that can occur during parsing, loading or validation
    of data structure.
    """

    VALIDATION_SEVERITIES = {
        errors.UnknownKey: dn.DataError.Severity.warning,
        errors.InvalidAbstractRecordType: dn.DataError.Severity.error,
        errors.InvalidOption: dn.DataError.Severity.error,
        errors.MissingAbstractRecordType: dn.DataError.Severity.error,
        errors.MissingKey: dn.DataError.Severity.error,
        errors.NotEnoughItems: dn.DataError.Severity.error,
        errors.TooManyItems: dn.DataError.Severity.error,
        errors.ValidationTypeError: dn.DataError.Severity.error,
        errors.ValueTooBig: dn.DataError.Severity.error,
        errors.ValueTooSmall: dn.DataError.Severity.error,
        errors.ValidationError: dn.DataError.Severity.error
    }

    def __init__(self):
        self._errors = []

    def clear(self):
        """clears the error buffer"""
        self._errors = []

    @property
    def errors(self):
        """Sorted array of errors."""
        return sorted(self._errors, key=lambda error: (
            error.span.start, -error.severity.value, error.category.value))

    def report_parsing_error(self, yaml_error, error_end_pos):
        """reports a YAML error that occurs during parsing"""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.fatal
        description = yaml_error.problem
        start_pos = dn.Position.from_yaml_error(yaml_error)
        span = dn.Span(start=start_pos, end=error_end_pos)
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_modification_ignored(self, start_line, end_line):
        """reports that modification of certain lines has been ignored"""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.info
        description = "Modifications ignored. Please fix parsing error(s) first."
        start_pos = dn.Position(start_line + 1, 1)
        end_pos = dn.Position(end_line + 1, 1)
        span = dn.Span(start=start_pos, end=end_pos)
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_validation_error(self, node, error):
        """
        reports an error that occurs during validation
        returns True when severity is error or greater, False otherwise
        """
        category = dn.DataError.Category.validation
        severity = self.VALIDATION_SEVERITIES[type(error)]
        description = str(error)
        span = get_validation_error_span(node, error)
        error = dn.DataError(category, severity, description, span, node)
        self._errors.append(error)
        return severity.value >= dn.DataError.Severity.error.value

    def report_invalid_reference_error(self, node):
        """reports an invalid reference path"""
        category = dn.DataError.Category.reference
        severity = dn.DataError.Severity.error
        description = "Referenced node '{path}' does not exist".format(path=node.ref)
        span = node.span
        error = dn.DataError(category, severity, description, span, node)
        self._errors.append(error)

    def report_multi_reference_error(self, node):
        """reports a multi-level reference error"""
        category = dn.DataError.Category.reference
        severity = dn.DataError.Severity.error
        description = "Multi-level reference not supported."
        span = node.span
        error = dn.DataError(category, severity, description, span, node)
        self._errors.append(error)

    def report_invalid_tag_position(self, tag):
        """Reports an invalid tag position error."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.info
        description = "Tag has no effect."
        span = tag.span
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_anchor_override(self, anchor, node):
        """Reports a duplicate anchor."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.info
        description = "Overriding anchor &{anchor} at {position}.".format(
            anchor=anchor.value,
            position=node.anchor.span.start
        )
        span = anchor.span
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_invalid_mapping_key(self, span):
        """Reports an invalid (non-scalar) key for mapping."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = "Only scalar keys are supported for records."
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_undefined_anchor(self, anchor):
        """Reports an undefined anchor used in alias."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = "Anchor &{anchor} is not defined.".format(
            anchor=anchor.value
        )
        error = dn.DataError(category, severity, description, anchor.span)
        self._errors.append(error)

    def report_merge_error(self, span):
        """Reports a merge error."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = "Only alias or an array of aliases can be merged."
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_invalid_merge_type(self, span):
        """Reports invalid merge type."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = "Invalid anchor node type. Only Record nodes can be merged."
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def report_construct_scalar_error(self, node, description):
        """Reports scalar node construction error."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        error = dn.DataError(category, severity, description, node.span, node)
        self._errors.append(error)

    def report_multiline_flow(self, node):
        """Reports scalar node construction error."""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.info
        description = "Multiline flow style usage is not recommended."
        error = dn.DataError(category, severity, description, node.span, node)
        self._errors.append(error)

def get_validation_error_span(node, error):
    """Determines the correct position of a validation error."""
    span = node.key.span
    if isinstance(error, errors.UnknownKey):
        span = node.get_child(error.key).key.span
    elif isinstance(error, errors.InvalidAbstractRecordType):
        span = node.type.span
    elif (isinstance(error, errors.InvalidOption) or
          isinstance(error, errors.ValueTooBig) or
          isinstance(error, errors.ValueTooSmall) or
          isinstance(error, errors.ValidationTypeError)):
        span = node.span
    elif isinstance(node, dn.ScalarNode):
        if isinstance(error, errors.ValidationTypeError):
            span = node.key.span
        else:
            span = node.span
    return span
