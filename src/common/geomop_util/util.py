"""
Utility classes.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""


class TextValue:
    """Represents a value in the input text."""
    def __init__(self, value=None):
        self.value = value
        """the value from input text"""
        self.span = None
        """:class:`.Span` specifies the position of value in input text"""


class Parameter:
    """A parameter in a config file."""
    def __init__(self, name=None, type=None, value=None):
        self.name = name
        self.type = type
        self.value = value


class File:
    """Represents a file entry in a config file."""
    def __init__(self, file_path, params=None, selected=False):
        self.file_path = file_path
        self.selected = selected
        if params is None:
            self.params = []
        else:
            self.params = params
