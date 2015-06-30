"""
Data Node package

Contains classes for representing the tree structure of config files.
"""

# from data.meconfig import MEConfig as cfg

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
        self.section = None
        """borders the position of this node in input text"""

    @property
    def options(self):
        """possible options to hint in autocomplete"""
        return []

    def get_node_at_mark(self, mark):
        """Retrieves DataNode at specified mark (line, column)."""
        raise NotImplementedError

    @property
    def info_text(self):
        """help text describing the input type"""
        raise NotImplementedError


class ArrayNode(DataNode):
    """Represents an array node in the tree structure."""
    def __init__(self, key=None, parent=None):
        super(ArrayNode, self).__init__(key, parent)
        self.children = []
        """list of children nodes"""

    def get_node_at_mark(self, mark):
        """Retrieves DataNode at specified mark (line, column)."""
        raise NotImplementedError


class RecordNode(DataNode):
    """Represents a record node in the tree structure."""
    def __init__(self, key=None, parent=None):
        super(RecordNode, self).__init__(key, parent)
        self.children = {}
        """dictionary of children nodes and their keys"""

    def get_node_at_mark(self, mark):
        """Retrieves DataNode at specified mark (line, column)."""
        raise NotImplementedError

    @property
    def options(self):
        """list of possible record keys for autocomplete"""
        raise NotImplementedError


class ScalarNode(DataNode):
    """Represents a scalar node in the tree structure."""
    def __init__(self, key=None, parent=None, value=None):
        super(ScalarNode, self).__init__(key, parent)
        self.value = value
        """the scalar value"""

    def get_node_at_mark(self, mark):
        """Retrieves DataNode at specified mark (line, column)."""
        raise NotImplementedError

    @property
    def options(self):
        """list of possible values for autocomplete"""
        raise NotImplementedError


class Key:
    """Represents a key in the tree structure."""
    def __init__(self, value=None):
        self.value = value
        """representation of the key"""
        self.section = None
        """:class:`.Section` borders the position of the key"""


class Position:
    """Marks a cursor position in text."""
    def __init__(self, mark):
        self.line = None
        """line number; starts from 1"""
        self.column = None
        """column number; starts from 1"""
        if mark is not None:
            self.line = mark.line + 1
            self.column = mark.column + 1


class Section:
    """Borders a part of text."""
    def __init__(self, start_mark=None, end_mark=None):
        self.start = Position(start_mark)
        """:class:`.Position` indicates the start of the section; inclusive"""
        self.end = Position(end_mark)
        """:class:`.Position` indicates the end of the section; exclusive"""
