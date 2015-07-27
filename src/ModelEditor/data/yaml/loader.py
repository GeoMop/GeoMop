"""Package for generating DataNode structure from YAML document."""

import yaml
from data.yaml.constructor import construct_scalar
from data.yaml.resolver import resolve_scalar_tag
from data import data_node as dn
import copy


class Loader:
    """Generates DataNode structure from YAML document."""
    def __init__(self):
        self._event = None
        self._events = None
        self._document = None
        self._reference_nodes = []

    def load(self, document):
        """Loads the YAML document and returns the root DataNode."""
        if document is None:
            return None
        self._document = document
        self._reference_nodes = []
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
        while (root is None or isinstance(root, dn.ScalarNode))\
                and self._event is not None:
            # skip non-node events (StreamStart, DocumentStart)
            self._parse_next_event()
            root = self._create_node()
        self._resolve_references()
        return root

    def _create_node(self, parent=None):
        node = None
        if hasattr(self._event, 'tag') and self._event.tag is not None:
            node = self._create_node_by_tag()
        elif isinstance(self._event, yaml.MappingStartEvent):
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
        node = dn.CompositeNode(True)
        start_mark = self._event.start_mark
        self._parse_next_event()
        while not isinstance(self._event, yaml.MappingEndEvent):
            if not isinstance(self._event, yaml.ScalarEvent):
                raise Exception('Complex keys are not supported for Records')
            key = dn.TextValue()
            key.value = self._event.value
            key.span = _get_span_from_marks(self._event.start_mark,
                                            self._event.end_mark)
            self._parse_next_event()
            child_node = self._create_node(node)  # recursively create children
            child_node.key = key
            node.children.append(child_node)
            self._parse_next_event()
        end_mark = self._event.end_mark
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_node_by_tag(self):
        """creates either an abstract record (for app specific tags: !) or
        scalar value of specified type (yaml tags - !!, tag:yaml.org,2002:)"""
        if self._event.tag.startswith('tag:yaml.org,2002:'):
            node = self._create_scalar_node()
        elif self._event.tag == '!ref':
            node = self._create_scalar_node()
            node.ref = node.value
            self._reference_nodes.append(node)
        else:  # abstract record
            node = self._create_abstract_record()
        return node

    def _create_abstract_record(self):
        type_ = self._get_node_type()
        if isinstance(self._event, yaml.MappingStartEvent):
            node = self._create_record_node()
        elif isinstance(self._event, yaml.ScalarEvent):
            temp_node = self._create_scalar_node()
            if temp_node.value is None:  # null - should be constructed as mapping instead
                node = dn.CompositeNode(True)
                node.span = temp_node.span
            else:  # keep ScalarNode - might be used for autoconversion
                node = temp_node
        node.type = type_
        return node

    def _get_node_type(self):
        """Create the node type from tag."""
        if self._event.tag[0] != '!':
            raise NotImplementedError("Tags with directive not supported yet")
        type_ = dn.TextValue()
        type_.value = self._event.tag[1:]
        start = dn.Position(self._event.start_mark.line + 1,
                            self._event.start_mark.column + 2)
        end = dn.Position(start.line, start.column + len(type_.value))
        type_.span = dn.Span(start, end)
        return type_

    def _create_array_node(self):
        node = dn.CompositeNode(False)
        start_mark = self._event.start_mark
        self._parse_next_event()
        while not isinstance(self._event, yaml.SequenceEndEvent):
            key = dn.TextValue()
            key.value = str(len(node.children))
            child_node = self._create_node(node)  # recursively create children
            child_node.key = key
            node.children.append(child_node)
            self._parse_next_event()
        end_mark = self._event.end_mark
        node.span = _get_span_from_marks(start_mark, end_mark)
        return node

    def _create_scalar_node(self):
        node = dn.ScalarNode()
        tag = self._event.tag
        if tag is None or not tag.startswith('tag:yaml.org,2002:'):
            tag = resolve_scalar_tag(self._event.value)
        node.value = construct_scalar(self._event.value, tag)
        node.span = _get_span_from_marks(self._event.start_mark,
                                         self._event.end_mark)
        if node.value is None:
            node.span.start.column += 1
            node.span.end.column += 1
        return node

    def _resolve_references(self):
        """replaces all reference nodes with copies of the data
        they point to"""
        for link_node in self._reference_nodes:
            try:
                actual_node = link_node.get_node_at_path(link_node.ref)
            except LookupError:
                # TODO buffer errors
                raise Exception("Referenced node '{path}' does not exist"
                                .format(path=link_node.ref))
            else:
                if actual_node.ref is not None:
                    raise Exception("Multi-level reference not supported")
                reference_node = copy.deepcopy(actual_node)
                reference_node.ref = link_node.ref
                reference_node.key = link_node.key
                link_node.parent.set_child(reference_node)


def _get_span_from_marks(start_mark, end_mark):
    start = dn.Position(start_mark.line + 1, start_mark.column + 1)
    end = dn.Position(end_mark.line + 1, end_mark.column + 1)
    return dn.Span(start, end)
