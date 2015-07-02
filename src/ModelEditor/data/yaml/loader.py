"""Package for generating DataNode structure from YAML document."""

import yaml
from data.yaml.constructor import construct_scalar
from data.yaml.resolver import resolve_scalar_tag
from data.data_node import RecordNode, ArrayNode, ScalarNode, Key, Span


class Loader:
    """Generates DataNode structure from YAML document."""
    def __init__(self):
        pass

    def load(self, document):
        """Loads the YAML document and returns the root DataNode."""
        if document is None:
            return None
        events = yaml.parse(document)
        root = self._create_root_node(events)
        return root

    def _create_root_node(self, events):
        root = None
        try:
            event = next(events)
            root = self._create_node(event, events)
            while root is None:
                event = next(events)
                root = self._create_node(event, events)
        except StopIteration:
            pass
        return root

    def _create_node(self, event, events, parent=None):
        node = None
        if isinstance(event, yaml.MappingStartEvent):
            node = self._create_record_node(event, events)
        elif isinstance(event, yaml.SequenceStartEvent):
            node = self._create_array_node(event, events)
        elif isinstance(event, yaml.ScalarEvent):
            node = self._create_scalar_node(event)
        if node is not None:
            node.parent = parent
        return node

    def _create_record_node(self, event, events):
        node = RecordNode()
        start_mark = event.start_mark
        event = next(events)
        while not isinstance(event, yaml.MappingEndEvent):
            if not isinstance(event, yaml.ScalarEvent):
                raise Exception('Complex keys are not supported for Records')
            key = Key()
            key.value = event.value
            key.section = Span(event.start_mark, event.end_mark)
            event = next(events)
            child_node = self._create_node(event, events)  # recursively create children
            child_node.key = key
            node.children[key.value] = child_node
            event = next(events)
        end_mark = event.end_mark
        node.section = Span(start_mark, end_mark)
        return node

    def _create_array_node(self, event, events):
        node = ArrayNode()
        start_mark = event.start_mark
        event = next(events)
        while not isinstance(event, yaml.SequenceEndEvent):
            key = Key()
            key.value = len(node.children)
            child_node = self._create_node(event, events)  # recursively create children
            child_node.key = key
            node.children.append(child_node)
            event = next(events)
        end_mark = event.end_mark
        node.section = Span(start_mark, end_mark)
        return node

    def _create_scalar_node(self, event):
        node = ScalarNode()
        tag = event.tag
        if tag is None:
            tag = resolve_scalar_tag(event.value)
        node.value = construct_scalar(event.value, tag)
        node.section = Span(event.start_mark, event.end_mark)
        return node
