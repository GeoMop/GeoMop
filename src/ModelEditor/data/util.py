"""
Utilities package for `data` package.
"""

__author__ = 'Tomas Krizek'

from enum import Enum

from .locators import Span, Position


class TextValue:
    """Represents a value in the input text."""
    def __init__(self, value=None):
        self.value = value
        """the value from input text"""
        self.span = None
        """:class:`.Span` specifies the position of value in input text"""


class DataError(Exception):
    """Represents an error that occurs while working with data."""

    class Category(Enum):
        """Defines the type of an error."""
        validation = 'Validation'
        yaml = 'Parsing'
        reference = 'Reference'

    class Severity(Enum):
        """Severity of an error."""
        info = 0
        warning = 1
        error = 2
        fatal = 3

    def __init__(self, category, severity, description, span, node=None):
        super(DataError, self).__init__(self)
        self.category = category
        """:class:`ErrorCategory` the category of error"""
        self.span = span
        """:class:`Span` the position of error"""
        if self.span is None:
            self.span = Span(start=Position(1, 1), end=Position(1, 1))
        self.description = description
        """describes the error"""
        self.node = node
        """:class:`DataNode` optional; the node where the error occurred"""
        self.severity = severity

    @property
    def title(self):
        """title of the error"""
        severities = {DataError.Severity.info: 'Info',
                      DataError.Severity.warning: 'Warning',
                      DataError.Severity.error: 'Error',
                      DataError.Severity.fatal: 'Fatal Error'}
        return "{category} {severity}".format(
            category=self.category.value,
            severity=severities[self.severity]
        )

    def __str__(self):
        text = "{span} {title}\n{description}"
        return text.format(
            span=self.span,
            title=self.title,
            description=self.description
        )
