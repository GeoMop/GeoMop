"""
Data Node package

Contains classes for representing the tree structure of config files.
"""

__author__ = 'Tomas Krizek'

from enum import Enum
from ist import InfoTextGenerator
from helpers.subyaml import CursorType

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
            self.key = TextValue()
        self.input_type = None
        """input type specified by format"""
        self.span = None
        """borders the position of this node in input text"""
        self.anchor = None
        """anchor of the node `TextValue`"""
        self.origin = Origin.structure
        """indicates how node was created"""
        self._options = []

    @property
    def absolute_path(self):
        """the absolute path to this node"""
        return self.generate_absolute_path()

    def generate_absolute_path(self, descendant_path=None):
        """generates absolute path to this node, used recursively"""
        if self.parent is None:
            if descendant_path is None:
                descendant_path = ""
            return "/" + descendant_path
        if descendant_path is None:
            path = str(self.key.value)
        else:
            path = str(self.key.value) + "/" + descendant_path
        return self.parent.generate_absolute_path(path)

    @property
    def options(self):
        """possible options to hint in autocomplete"""
        options = self._options
        # if DEBUG_MODE and self.span is not None:
        #     # return start, end position as options
        #     options = ["start: {start}".format(start=self.span.start),
        #                "end: {end}".format(end=self.span.end)]
        return options

    @options.setter
    def options(self, options):
        """Autocomplete options setter."""
        self._options = options

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        raise NotImplementedError

    def is_child_on_line(self, line):
        """
        Return if in set line is some child
        """
        return False

    def get_node_at_path(self, path):
        """returns node at given path"""
        # pylint: disable=no-member
        if path is None:
            raise LookupError("No path provided")
        node = self
        if path.startswith(self.absolute_path):  # absolute path
            path = path[len(self.absolute_path):]
        elif path.startswith('/'):  # absolute path with different location
            while node.parent is not None:
                node = node.parent  # crawl up to root

        for key in path.split('/'):
            if not key or key == '.':
                continue
            elif key == '..':
                node = node.parent
                continue
            if not isinstance(node, CompositeNode) or node.get_child(key) is None:
                raise LookupError("Node {key} does not exist in {location}"
                                  .format(key=key, location=node.absolute_path))
            node = node.get_child(key)
        return node

    def get_info_text(self, cursor_type=CursorType.value):
        """Returns help text describing the input type based on cursor_type."""
        input_type = None
        selected = None

        # crawl up to the first "real" node (present in text structure)
        prev_node = self
        node = self
        while node.origin != Origin.structure:
            prev_node = node
            node = node.parent

        # select input_type based on cursor_type
        if cursor_type == CursorType.key.value:
            if node.parent is not None and node.parent.input_type is not None:
                input_type = node.parent.input_type
                selected = node.key.value
        elif cursor_type == CursorType.tag.value:
            if node.parent is not None and node.parent.input_type is not None:
                input_type = node.parent.input_type['keys'][node.key.value]['type']
                selected = getattr(node, 'type', None)
        else:  # default behavior - for value and others
            input_type = node.input_type
            if node.input_type and node.input_type['base_type'] == 'Selection':
                selected = prev_node.value
            else:
                selected = prev_node.key.value

        if input_type is None:
            # unknown node -> show closest available parent input type
            while node is not None and node.input_type is None:
                node = node.parent
            input_type = node.input_type

        # show info for Record, Selection or AbstractRecord that is in input structure
        while (input_type['base_type'] not in ['Record', 'Selection', 'AbstractRecord']
               or node.origin != Origin.structure):
            prev_node = node
            node = node.parent
            input_type = node.input_type
            selected = prev_node.key.value
        return InfoTextGenerator.get_info_text(input_type, selected=selected)

    def __str__(self):
        text = (
            "{type_} at 0x{address:x}\n"
            "  key: {key}\n"
            "  parent: {parent_type} at 0x{parent_address:x}\n"
            "  ref: {ref}\n"
            "  span: {span}\n"
            "  input_type: {input_type}\n"
        )
        return text.format(
            type_=type(self).__name__,
            address=id(self),
            key=self.key.value,
            parent_type=type(self.parent).__name__,
            parent_address=id(self.parent),
            ref=self.ref,
            span=self.span,
            input_type=self.input_type
        )

    @property
    def start(self):
        """start of node, including its key"""
        start = self.span.start
        if self.key is not None and self.key.span is not None:
            start = self.key.span.start
        return start

    @property
    def end(self):
        """Returns the end of this node."""
        return self.span.end


class CompositeNode(DataNode):
    """Represents a composite node in the tree structure."""
    def __init__(self, explicit_keys, key=None, parent=None):
        super(CompositeNode, self).__init__(key, parent)
        self.children = []
        """list of children nodes"""
        self.explicit_keys = explicit_keys
        """boolean; indicates whether keys are specified (record) or
        implicit (array)"""
        self.type = None
        """specifies the type of AbstractRecord"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        node = None
        if self.start <= position <= self.end:
            node = self
            for child in self.children:
                descendant = child.get_node_at_position(position)
                if descendant is not None:
                    node = descendant
                    break
        return node

    def __str__(self):
        text = super(CompositeNode, self).__str__()
        children_keys = [str(child.key.value) for child in self.children]
        text += "  children_keys: {children_keys}\n".format(
            children_keys=', '.join(children_keys)
        )
        return text

    def get_child(self, key):
        """
        Returns a child node for the given key; None if key doesn't
        exist.
        """
        for child in self.children:
            if key == child.key.value:
                return child
        return None

    def set_child(self, node):
        """
        Sets the specified node as child of this node. If the key already
        exists, the other child node is replaced by this child_node.
        """
        node.parent = self

        for i, child in enumerate(self.children):
            if child.key.value == node.key.value:
                self.children[i] = node
                return
        # still not ended - new key
        self.children.append(node)

    def is_child_on_line(self, line):
        """
        Return if in set line is some child
        """
        for child in self.children:
            if child.start.line <= line and child.end.line >= line:
                return True
        return False

    @property
    def children_keys(self):
        """Returns all children keys."""
        return [child.key.value for child in self.children]


class ScalarNode(DataNode):
    """Represents a scalar node in the tree structure."""
    def __init__(self, key=None, parent=None, value=None):
        super(ScalarNode, self).__init__(key, parent)
        self.value = value
        """the scalar value"""

    def get_node_at_position(self, position):
        """Retrieves DataNode at specified position."""
        if self.start <= position <= self.end:
            return self
        return None

    def __str__(self):
        text = super(ScalarNode, self).__str__()
        text += "  value: {value}".format(
            value=self.value
        )
        return text


class TextValue:
    """Represents a value in the input text."""
    def __init__(self, value=None):
        self.value = value
        """the value from input text"""
        self.span = None
        """:class:`.Span` specifies the position of value in input text"""


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

    def __str__(self):
        return "[{line}:{column}]".format(line=self.line, column=self.column)

    @staticmethod
    def from_mark(mark):
        """Returns a `Position` from YAML mark."""
        return Position(mark.line + 1, mark.column + 1)

    @staticmethod
    def from_document_end(document):
        """Returns the last `Position` in the document."""
        lines = document.splitlines()
        line = len(lines)
        column = len(lines[line-1])
        return Position(line, column + 1)

    @staticmethod
    def from_yaml_error(yaml_error):
        """Returns a `Position` from `MarkedYAMLError`."""
        if yaml_error.problem_mark is not None:
            return Position.from_mark(yaml_error.problem_mark)
        else:
            return Position.from_mark(yaml_error.context_mark)


class Span:
    """Borders a part of text."""

    def __init__(self, start=None, end=None):
        self.start = start
        """:class:`.Position` indicates the start of the section; inclusive"""
        self.end = end
        """:class:`.Position` indicates the end of the section; exclusive"""

    def __str__(self):
        return "{start}-{end}".format(
            start=self.start,
            end=self.end
        )

    @staticmethod
    def from_event(event):
        """Constructs `Span` from YAML `event`."""
        return Span.from_marks(event.start_mark, event.end_mark)

    @staticmethod
    def from_marks(start_mark, end_mark):
        """Constructs `Span` from YAML marks."""
        start = Position.from_mark(start_mark)
        end = Position.from_mark(end_mark)
        return Span(start, end)


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


class Origin(Enum):
    """The origin of data node."""
    structure = 1
    ac_array = 2
    ac_reducible_to_key = 3
