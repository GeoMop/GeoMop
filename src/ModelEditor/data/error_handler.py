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
        return list(self._errors)

    def report_parsing_error(self, yaml_error, error_end_pos):
        """reports a YAML error that occurs during parsing"""
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = yaml_error.problem
        error_line = get_error_line_from_yaml_error(yaml_error) + 1
        start_pos = dn.Position(error_line, 1)
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
        description = "Multi-level reference not supported"
        span = node.span
        error = dn.DataError(category, severity, description, span, node)
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


def get_error_line_from_yaml_error(yaml_error):
    if yaml_error.problem_mark is not None:
        line = yaml_error.problem_mark.line
    else:
        line = yaml_error.context_mark.line
    return line
