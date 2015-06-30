"""
Data Node package

Contains classes for representing the tree structure of config files.
"""

from data.meconfig import MEConfig as cfg

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
        self.start_mark = (None, None)
        """position where the node starts; (line, column) tuple"""
        self.end_mark = (None, None)
        """position where the node ends; (line, column) tuple"""
        self.input_type = None
        """input type specified by format"""
        self.options = []

    def get_node_at_mark(self, mark):
        """Retrieves DataNode at specified mark (line, column)."""
        raise NotImplementedError

    @property
    def documentation(self):
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
        self.options = []
        """list of possible keys for autocomplete"""

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
        """representation of the key"""
        self.start_mark = (None, None)
        """position where the value starts"""
        self.end_mark = (None, None)
        """position where the value ends"""

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
        self.start_mark = (None, None)
        """position where the key starts"""
        self.end_mark = (None, None)
        """position where the key ends"""
