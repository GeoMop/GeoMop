"""Package for generating DataNode structure from YAML document."""

import yaml
from data.yaml.constructor import construct_scalar
from data.yaml.resolver import resolve_scalar_tag
from data.data_node import (CompositeNode, ScalarNode, Key, Span,
                            Position)


class Loader:
    """Generates DataNode structure from YAML document."""
    def __init__(self):
        self._event = None
        self._events = None
        self._document = None

    def load(self, document):
        """Loads the YAML document and returns the root DataNode."""
        if document is None:
            return None
        self._document = document
        self._events = yaml.parse(self._document)
        root = self._create_root_node()
        return root

    def _parse_next_event(self):
        try:
            self._event = next(self._events)
        except yaml.MarkedYAMLError as error:
            raise error
        except StopIteration:
            self._event = None

    def _create_root_node(self):
        self._parse_next_event()
        root = self._create_node()
        while (root is None or isinstance(root, ScalarNode))\
                and self._event is not None:
            # skip non-node events (StreamStart, DocumentStart)
            self._parse_next_event()
            root = self._create_node()
        return root

    def _create_node(self, parent=None):
        node = None
        if isinstance(self._event, yaml.MappingStartEvent):
            node = self._create_record_node()
        elif isinstance(self._event, yaml.SequenceStartEvent):
            node = self._create_array_node()
        elif isinstance(self._event, yaml.ScalarEvent):
            node = self._create_scalar_node()
        elif isinstance(self._event, yaml.AliasEvent):
            raise NotImplementedError
        if node is not None:
            node.parent = parent
        return node

    def _create_record_node(self):
        node = CompositeNode(True)
        if self._event.tag is not None:
            node.children.append(self._create_type_node())
        start_mark = self._event.start_mark
        self._parse_next_event()
        while not isinstance(self._event, yaml.MappingEndEvent):
            if not isinstance(self._event, yaml.ScalarEvent):
                raise Exception('Complex keys are not supported for Records')
            key = Key()
            key.value = self._event.value
            key.section = _get_span_from_marks(self._event.start_mark,
                                               self._event.end_mark)
            self._parse_next_event()
            child_node = self._create_node(node)  # recursively create children
            child_node.key = key
            node.children.append(child_node)
            self._parse_next_event()
        end_mark = self._event.end_mark
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_type_node(self):
        """Creates a TYPE node from tag."""
        if self._event.tag[0] == '!':
            tag = self._event.tag[1:]
            start = Position(self._event.start_mark.line + 1,
                             self._event.start_mark.column + 2)
            end = Position(start.line,
                           start.column + len(tag))
        else:
            raise NotImplementedError("Tags with directive not supported yet")
        node = ScalarNode()
        node.key = Key()
        node.key.value = 'TYPE'
        node.value = tag
        node.span = Span(start, end)
        return node

    def _create_array_node(self):
        node = CompositeNode(False)
        start_mark = self._event.start_mark
        self._parse_next_event()
        while not isinstance(self._event, yaml.SequenceEndEvent):
            key = Key()
            key.value = len(node.children)
            child_node = self._create_node(node)  # recursively create children
            child_node.key = key
            node.children.append(child_node)
            self._parse_next_event()
        end_mark = self._event.end_mark
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_scalar_node(self):
        node = ScalarNode()
        tag = self._event.tag
        if tag is None:
            tag = resolve_scalar_tag(self._event.value)
        node.value = construct_scalar(self._event.value, tag)
        node.span = _get_span_from_marks(self._event.start_mark,
                                         self._event.end_mark)
        if node.value is None:
            node.span.start.column += 1
            node.span.end.column += 1
        return node


def _get_span_from_marks(start_mark, end_mark):
    start = Position(start_mark.line + 1, start_mark.column + 1)
    end = Position(end_mark.line + 1, end_mark.column + 1)
    return Span(start, end)
