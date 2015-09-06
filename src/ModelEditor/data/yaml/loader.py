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
        self._fatal_error_node = None
        self.anchors = {}
        self.error_handler = error_handler
        if self.error_handler is None:
            self.error_handler = ErrorHandler()

    def load(self, document):
        """Loads the YAML document and returns the root DataNode."""
        if document is None:
            return None
        self._fatal_error_node = None
        self._iterate_events = True
        self.anchors = {}
        self._document = document
        self._event_generator = pyyaml.parse(self._document)

        self._next_parse_event()  # StreamStartEvent
        self._next_parse_event()  # DocumentStartEvent
        self._next_parse_event()  # first actual event

        root = self._create_node()
        if self._fatal_error_node:
            if isinstance(root, dn.CompositeNode):
                # pylint: disable=no-member
                root.set_child(self._fatal_error_node)
                root.span.end = self._fatal_error_node.end
        return root

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
                end_pos = dn.Position.from_document_end(self._document)
                self.error_handler.report_parsing_error(error, end_pos)
                self._create_fatal_error_node(error, end_pos)
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
        if value is None or value in ['*', '&']:
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
        if value is None or value == '!':
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
        line_index = start_mark.line
        line = lines[line_index]
        line = line[start_mark.column:]  # first line offset
        expr = '[{symbol}]([a-zA-Z0-9_:-]+)'.format(symbol=symbol)
        regex = re.compile(expr)

        match = regex.search(line)
        if match is not None:  # set correct offset of match
            start_column = start_mark.column + match.start(1)
            end_column = start_mark.column + match.end(1)

        while match is None and line_index < len(lines) - 1:
            line_index += 1
            line = lines[line_index]
            match = regex.search(line)

        start_column = locals().get('start_column', match.start(1))
        end_column = locals().get('end_column', match.end(1))
        start = dn.Position(line_index + 1, start_column + 1)
        end = dn.Position(line_index + 1, end_column + 1)
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
        node.span = dn.Span.from_event(self._event)
        try:
            node.value = construct_scalar(self._event.value, tag)
        except Exception as error:
            description = error.args[0]
            self.error_handler.report_construct_scalar_error(node, description)
            return node
        if node.value is None:
            # alter position of empty node (so it can be selected)
            node.span.end.column += 1
        return node

    def _create_abstract_record(self, tag):
        """Creates abstract record from parsing events."""
        invalid_position = False
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
            else:  # not null - tag has no effect
                node = temp_node
                invalid_position = True
        else:
            # someone tried to use tag for a sequence - tag has no effect
            node = self._create_array_node()
            invalid_position = True
        if invalid_position:
            self.error_handler.report_invalid_tag_position(tag)
        else:
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
            elif key.value == '<<':  # handle merge
                self._perform_merge(key, node)
                self._next_parse_event()
                continue
            if self._event is None:
                break  # something went wrong, abandon ship!
            child_node = self._create_node(node)
            self._next_parse_event()
            if child_node is None:  # i.e. unresolved alias
                continue
            child_node.key = key
            node.set_child(child_node)
        if self._event is not None:  # update end_mark when map ends correctly
            end_mark = self._event.end_mark
        elif node.children:
            end_mark = node.children[-1].span.end
            end_mark.line -= 1
            end_mark.column -= 1
        node.span = dn.Span.from_marks(start_mark, end_mark)
        return node

    def _create_record_key(self):
        """Creates `TextValue` of record key."""
        # check if key is scalar
        if not isinstance(self._event, pyyaml.ScalarEvent):
            span = dn.Span.from_event(self._event)
            self.error_handler.report_invalid_mapping_key(span)
            return None
        key = dn.TextValue()
        key.value = self._event.value
        key.span = dn.Span.from_event(self._event)
        return key

    def _perform_merge(self, key, node):
        """Performs merge operation on record node."""
        if isinstance(self._event, pyyaml.SequenceStartEvent):
            self._next_parse_event()
            while (self._event is not None and
                   not isinstance(self._event, pyyaml.SequenceEndEvent)):
                self._merge_into_node(key, node)
                self._next_parse_event()
        else:
            self._merge_into_node(key, node)

    def _merge_into_node(self, key, node):
        """Merges a single alias node into this record node."""
        # allow only alias nodes to be merged
        if not isinstance(self._event, pyyaml.AliasEvent):
            self._create_node(node)  # skip the node to avoid parsing error
            self.error_handler.report_merge_error(key.span)
            return

        anchor = self._extract_anchor()
        if anchor.value not in self.anchors:
            self.error_handler.report_undefined_anchor(anchor)
            return

        anchor_node = self.anchors[anchor.value]
        # check if anchor_node is a record (mapping)
        not_composite = not isinstance(anchor_node, dn.CompositeNode)
        if not_composite or not anchor_node.explicit_keys:
            self.error_handler.report_invalid_merge_type(anchor.span)
            return

        for child in anchor_node.children:
            if child.key.value not in node.children_keys:
                node.set_child(copy.deepcopy(child))
        return

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
        node.span = dn.Span.from_marks(start_mark, end_mark)
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

        # set correct node.span
        node.span = copy.deepcopy(node.anchor.span)
        start = node.span.start
        node.span.start = dn.Position(start.line, start.column - 1)
        return node

    def _register_anchor(self, anchor, node):
        """Registers an anchor to a node."""
        node.anchor = anchor
        if anchor.value in self.anchors:
            self.error_handler.report_anchor_override(anchor, node)
        self.anchors[anchor.value] = node

    def _create_fatal_error_node(self, error, document_end_pos):
        """
        Creates a non-existing node in the data tree
        to wrap the content of the error (span) in a node.
        """
        # TODO Isn't this temporary solution?
        node = dn.ScalarNode()
        document_start_pos = dn.Position.from_yaml_error(error)
        node.span = dn.Span(document_start_pos, document_end_pos)
        node.key = dn.TextValue('fatal_error')
        self._fatal_error_node = node
