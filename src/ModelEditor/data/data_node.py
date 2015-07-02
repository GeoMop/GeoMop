"""
Data Node package

Contains classes for representing the tree structure of config files.
"""

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
            return self.key.value
        return ''


class ArrayNode(DataNode):
    """Represents an array node in the tree structure."""
    def __init__(self, key=None, parent=None):
        super(ArrayNode, self).__init__(key, parent)
        self.children = []
        """list of children nodes"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        node = None
        if self.span.start <= position < self.span.end:
            node = self
            for child in self.children:
                descendant = child.get_node_at_position(position)
                if descendant is not None:
                    node = descendant
                    break
        return node


class RecordNode(DataNode):
    """Represents a record node in the tree structure."""
    def __init__(self, key=None, parent=None):
        super(RecordNode, self).__init__(key, parent)
        self.children = {}
        """dictionary of children nodes and their keys"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        node = None
        if self.span.start <= position < self.span.end:
            node = self
            # pylint: disable=invalid-name, unused-variable
            for __, child in self.children.items():
                descendant = child.get_node_at_position(position)
                if descendant is not None:
                    node = descendant
                    break
        return node

    @property
    def options(self):
        """list of possible record keys for autocomplete"""
        if DEBUG_MODE:
            return super(RecordNode, self).options
        raise NotImplementedError


class ScalarNode(DataNode):
    """Represents a scalar node in the tree structure."""
    def __init__(self, key=None, parent=None, value=None):
        super(ScalarNode, self).__init__(key, parent)
        self.value = value
        """the scalar value"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        if self.span.start <= position <= self.span.end:
            return self
        return None

    @property
    def options(self):
        """list of possible values for autocomplete"""
        if DEBUG_MODE:
            return super(RecordNode, self).options
        raise NotImplementedError


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
