"""
Data Node package

Contains classes for representing the tree structure of config files.
"""

from enum import Enum

DEBUG_MODE = True
"""changes the behaviour to debug mode"""


class DataNode:
    """
    Represents a node in the tree structure.

    The complete tree is represented by its root node.
    """
    def __init__(self, key=None, parent=None):
        self.ref = None
        """reference to another node"""
        self.parent = parent
        """parent node"""
        self.key = key
        """key (name) of this node"""
        if self.key is None:
            self.key = Key()
        self.input_type = None
        """input type specified by format"""
        self.span = None
        """borders the position of this node in input text"""

    @property
    def options(self):
        """possible options to hint in autocomplete"""
        options = []
        if DEBUG_MODE:
            # return start, end position as options
            options.append("start: {line}:{column}"
                           .format(line=self.span.start.line,
                                   column=self.span.start.column))
            options.append("end: {line}:{column}"
                           .format(line=self.span.end.line,
                                   column=self.span.end.column))
        return options

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        raise NotImplementedError

    @property
    def info_text(self):
        """help text describing the input type"""
        if DEBUG_MODE:
            return str(self).replace("\n", "<br/>")
        return ''

    def __str__(self):
        text = (
            "{type_} at 0x{address:x}\n"
            "  key: {key}\n"
            "  parent: {parent_type} at 0x{parent_address:x}\n"
            "  ref: {ref}\n"
            "  span: {sline}:{scol}-{eline}:{ecol}\n"
            "  input_type: {input_type}\n"
        )
        return text.format(
            type_=type(self).__name__,
            address=id(self),
            key=self.key.value,
            parent_type=type(self.parent).__name__,
            parent_address=id(self.parent),
            ref=self.ref,
            sline=self.span.start.line,
            scol=self.span.start.column,
            eline=self.span.end.line,
            ecol=self.span.end.column,
            input_type=self.input_type
        )

    @property
    def _beginning(self):
        """beginning of node, including its key"""
        beginning = self.span.start
        if self.key is not None and self.key.section is not None:
            beginning = self.key.section.start
        return beginning

    @property
    def _end(self):
        return self.span.end


class CompositeNode(DataNode):
    """Represents a composite node in the tree structure."""
    def __init__(self, explicit_keys, key=None, parent=None):
        super(CompositeNode, self).__init__(key, parent)
        self.children = []
        """list of children nodes"""
        self.explicits_keys = explicit_keys
        """boolean; indicates whether keys are specified (record) or
        implicit (array)"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        node = None
        if self._beginning <= position < self._end:
            node = self
            for child in self.children:
                descendant = child.get_node_at_position(position)
                if descendant is not None:
                    node = descendant
                    break
        return node

    def __str__(self):
        text = super(CompositeNode, self).__str__()
        children_keys = [child.key.value for child in self.children]
        text += "  children_keys: {children_keys}\n".format(
            children_keys=', '.join(str(children_keys))
        )
        return text

    @property
    def options(self):
        """list of possible record keys for autocomplete"""
        if not self.explicits_keys:
            return []
        if DEBUG_MODE:
            return super(CompositeNode, self).options
        raise NotImplementedError


class ScalarNode(DataNode):
    """Represents a scalar node in the tree structure."""
    def __init__(self, key=None, parent=None, value=None):
        super(ScalarNode, self).__init__(key, parent)
        self.value = value
        """the scalar value"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        if self._beginning <= position <= self._end:
            return self
        return None

    @property
    def options(self):
        """list of possible values for autocomplete"""
        if DEBUG_MODE:
            return super(ScalarNode, self).options
        raise NotImplementedError

    def __str__(self):
        text = super(ScalarNode, self).__str__()
        text += "  value: {value}".format(
            value=self.value
        )
        return text


class Key:
    """Represents a key in the tree structure."""
    def __init__(self, value=None):
        self.value = value
        """representation of the key"""
        self.section = None
        """:class:`.Section` borders the position of the key"""


class ComparableMixin:
    """
    Utility class -- implements other rich comparison operators
    based on < (less than).
    """
    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self


class Position(ComparableMixin):
    """Marks a cursor position in text."""
    def __init__(self, line=None, column=None):
        self.line = line
        """line number; starts from 1"""
        self.column = column
        """column number; starts from 1"""

    def __lt__(self, other):
        if self.line < other.line:
            return True
        elif self.line == other.line:
            return self.column < other.column
        return False


class Span:
    """Borders a part of text."""
    def __init__(self, start=None, end=None):
        self.start = start
        """:class:`.Position` indicates the start of the section; inclusive"""
        self.end = end
        """:class:`.Position` indicates the end of the section; exclusive"""


class ErrorCategory(Enum):
    """Defines the type of an error."""
    validation = 'Validation Error'
    yaml = 'Parsing Error'


class DataError(Exception):
    """Represents an error that occurs while working with data."""
    def __init__(self, category, description, position, node=None):
        self.category = category
        """:class:`ErrorCategory` the category of error"""
        self.position = position
        """:class:`Position` the position of error"""
        self.description = description
        """describes the error"""
        self.node = node
        """:class:`DataNode` optional; the node where the error occurred"""

    def __str__(self):
        text = "{line}:{column} - {name}\n{description}"
        return text.format(
            line=self.position.line,
            column=self.position.column,
            name=self.category.value,
            description=self.description
        )

    @classmethod
    def from_marked_yaml_error(cls, yaml_error):
        """Creates DataError from MarkedYAMLError."""
        if yaml_error.problem_mark is not None:
            line = yaml_error.problem_mark.line
            column = yaml_error.problem_mark.column
        else:
            line = yaml_error.context_mark.line
            column = yaml_error.context_mark.column
        position = Position(line + 1, column + 1)
        return DataError(ErrorCategory.yaml, yaml_error.problem, position)
