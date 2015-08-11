"""
Package for generating DataNode structure from YAML document.

Author: Tomas Krizek
"""

import yaml as pyyaml
from data.yaml.constructor import construct_scalar
from data.yaml.resolver import resolve_scalar_tag
from data.error_handler import ErrorHandler
from data import data_node as dn
import re
import copy


class Loader:
    """Generates DataNode structure from YAML document."""
    def __init__(self, error_handler=None):
        """Initializes the loader with ErrorHandler."""
        self._event = None
        self._event_generator = iter([])
        self._document = None
        self._iterate_events = True
        self.anchors = {}
        self.error_handler = error_handler
        if self.error_handler is None:
            self.error_handler = ErrorHandler()

    def load(self, document):
        """Loads the YAML document and returns the root DataNode."""
        if document is None:
            return None
        self._iterate_events = True
        self.anchors = {}
        self._document = document
        self._event_generator = pyyaml.parse(self._document)

        self._next_parse_event()  # StreamStartEvent
        self._next_parse_event()  # DocumentStartEvent
        self._next_parse_event()  # first actual event

        return self._create_node()

    def _next_parse_event(self):
        """
        Attempts to get next parsing event and handles errors. When there
        are no more valid parsing events, event is set to None.
        """
        if self._iterate_events:
            try:
                # get next parsing event
                self._event = next(self._event_generator)
            except pyyaml.MarkedYAMLError as error:
                # handle parsing error
                self._event = None
                self._iterate_events = False
                end_pos = get_document_end_position(self._document)
                self.error_handler.report_parsing_error(error, end_pos)
            except StopIteration:
                # handle end of parsing events
                self._event = None
                self._iterate_events = False

    def _create_node(self, parent=None):
        """Create a DataNode from parsing events."""
        anchor = self._extract_anchor()
        tag = self._extract_tag()
        node = None
        if tag is not None:
            node = self._create_node_by_tag(tag)
        elif isinstance(self._event, pyyaml.MappingStartEvent):
            node = self._create_record_node()
        elif isinstance(self._event, pyyaml.SequenceStartEvent):
            node = self._create_array_node()
        elif isinstance(self._event, pyyaml.ScalarEvent):
            node = self._create_scalar_node()
        elif isinstance(self._event, pyyaml.AliasEvent):
            node = self._create_alias_node(anchor)
        if node is not None:
            node.parent = parent
            # register anchor if it exists and node is not an alias
            if anchor is not None and node.ref is None:
                self._register_anchor(anchor, node)
        return node

    def _extract_anchor(self):
        """Extracts `TextValue` of anchor from the current event."""
        value = getattr(self._event, 'anchor', None)
        if value is None:
            return None
        anchor = dn.TextValue(value)
        symbol = '&'
        if isinstance(self._event, pyyaml.AliasEvent):
            symbol = '*'
        anchor.span = self._extract_property_span(self._event.start_mark, symbol)
        return anchor

    def _extract_tag(self):
        """Extracts `TextValue` of tag from the current event."""
        value = getattr(self._event, 'tag', None)
        if value is None:
            return None
        tag = dn.TextValue(value)
        tag.span = self._extract_property_span(self._event.start_mark, '!')
        return tag

    def _extract_property_span(self, start_mark, symbol):
        """
        Create a `Span` from the first `symbol` at `start_mark`.
        Used to get the span of node properties like anchors or tags.
        """
        # set document to start at start_mark
        lines = self._document.splitlines()
        document = '\n'.join(lines[start_mark.line:])
        document = document[start_mark.column:]

        current_line = start_mark.line
        current_column = start_mark.column
        end_line = None
        end_column = None
        symbol_found = False
        space_regex = re.compile(r'\s')

        # find symbol and the span of the associated value
        for char in document:
            if char == symbol:
                symbol_found = True
                start_line = current_line
                start_column = current_column + 1  # exclude position of the symbol itself
            elif symbol_found:
                if space_regex.match(char):  # when whitespace is found
                    end_line = current_line
                    end_column = current_column
                    break
            if char == '\n':
                current_line += 1
                current_column = 0
                continue
            current_column += 1

        if symbol_found and end_line is None:
            end_line = current_line
            end_column = current_column
        start = dn.Position(start_line + 1, start_column + 1)
        end = dn.Position(end_line + 1, end_column + 1)
        return dn.Span(start, end)

    def _create_node_by_tag(self, tag):
        """
        Creates either an abstract record (for app specific tags: !) or
        scalar value of specified type (yaml tags - !!, tag:yaml.org,2002:)
        """
        if tag.value.startswith('tag:yaml.org,2002:'):
            node = self._create_scalar_node()
        else:  # abstract record
            node = self._create_abstract_record(tag)
        return node

    def _create_scalar_node(self):
        """Creates a ScalarNode."""
        node = dn.ScalarNode()
        tag = self._event.tag
        if tag is None or not tag.startswith('tag:yaml.org,2002:'):
            tag = resolve_scalar_tag(self._event.value)
        node.value = construct_scalar(self._event.value, tag)
        node.span = _get_span_from_marks(self._event.start_mark,
                                         self._event.end_mark)
        if node.value is None:
            # alter position of the node
            # TODO does it make sense?
            node.span.start.column += 1
            node.span.end.column += 1
        return node

    def _create_abstract_record(self, tag):
        """Creates abstract record from parsing events."""
        tag.value = tag.value[1:]  # remove leading !
        if isinstance(self._event, pyyaml.MappingStartEvent):
            # classic abstract record node
            node = self._create_record_node()
        elif isinstance(self._event, pyyaml.ScalarEvent):
            # scalar abstract node - either empty, or for autoconversion
            temp_node = self._create_scalar_node()
            if temp_node.value is None:
                # empty node - construct as mapping
                node = dn.CompositeNode(True)
                node.span = temp_node.span
            else:  # not null - keep ScalarNode (used for autoconversion)
                node = temp_node
        else:
            # someone tried to use tag for a sequence
            self.error_handler.report_invalid_tag_position(tag)
            return self._create_array_node()
        node.type = tag
        return node

    def _create_record_node(self):
        """Creates a record node."""
        node = dn.CompositeNode(True)
        start_mark = self._event.start_mark
        end_mark = self._event.end_mark
        self._next_parse_event()
        # create children
        while (self._event is not None and
               not isinstance(self._event, pyyaml.MappingEndEvent)):
            key = self._create_record_key()
            self._next_parse_event()  # value event
            if not key:  # if key is invalid
                continue
            if self._event is None:
                break  # something went wrong, abandon ship!
            child_node = self._create_node(node)
            self._next_parse_event()
            if child_node is None:  # i.e. unresolved alias
                continue
            child_node.key = key
            node.children.append(child_node)
        if self._event is not None:  # update end_mark when map ends correctly
            end_mark = self._event.end_mark
        elif node.children:
            end_mark = node.children[-1].span.end
            end_mark.line -= 1
            end_mark.column -= 1
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_record_key(self):
        """Creates `TextValue` of record key."""
        # check if key is scalar
        if not isinstance(self._event, pyyaml.ScalarEvent):
            span = _get_span_from_marks(self._event.start_mark,
                                        self._event.end_mark)
            self.error_handler.report_invalid_mapping_key(span)
            return None
        key = dn.TextValue()
        key.value = self._event.value
        key.span = _get_span_from_marks(self._event.start_mark,
                                        self._event.end_mark)
        return key

    def _create_array_node(self):
        """Creates an array node."""
        node = dn.CompositeNode(False)
        start_mark = self._event.start_mark
        end_mark = self._event.end_mark
        self._next_parse_event()
        while (self._event is not None and
               not isinstance(self._event, pyyaml.SequenceEndEvent)):
            key = dn.TextValue(str(len(node.children)))
            child_node = self._create_node(node)
            self._next_parse_event()
            if child_node is None:  # i.e. unresolved alias
                continue
            child_node.key = key
            node.children.append(child_node)
        if self._event is not None:  # update end_mark when array ends correctly
            end_mark = self._event.end_mark
        elif node.children:
            end_mark = node.children[-1].span.end
            end_mark.line -= 1
            end_mark.column -= 1
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_alias_node(self, anchor):
        """Creates an alias node."""
        if anchor.value not in self.anchors:
            self.error_handler.report_undefined_anchor(anchor)
            return None
        ref = self.anchors[anchor.value]
        node = copy.deepcopy(ref)
        node.anchor = anchor
        node.ref = ref
        # TODO verify or set node.span
        return node

    def _register_anchor(self, anchor, node):
        """Registers an anchor to a node."""
        node.anchor = anchor
        if anchor.value in self.anchors:
            self.error_handler.report_anchor_override(anchor, node)
        self.anchors[anchor.value] = node


def _get_span_from_marks(start_mark, end_mark):
    """Returns the `Span` from YAML Marks."""
    start = dn.Position(start_mark.line + 1, start_mark.column + 1)
    end = dn.Position(end_mark.line + 1, end_mark.column + 1)
    return dn.Span(start, end)


def get_document_end_position(document):
    """Returns the last `Position` in the document."""
    lines = document.splitlines()
    line = len(lines)
    column = len(lines[line-1])
    return dn.Position(line, column + 1)
