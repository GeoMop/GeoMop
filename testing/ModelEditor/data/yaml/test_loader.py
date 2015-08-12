"""
Tests for customized YAML loader.

Author: Tomas Krizek
"""
from data.yaml import Loader
from unittest.mock import Mock

# pylint: disable=protected-access


def test_anchor_alias():
    """Tests the YAML reference using anchor-alias."""
    doc = (
        "map: &map\n"
        "  value: &val 42\n"
        "  sequence: &seq\n"
        "    - 1\n"
        "    - 2\n"
        "map2: *map\n"
        "seq2: *seq\n"
        "val2: *val"
    )
    loader = Loader()
    root = loader.load(doc)
    equal_values = [
        ('/map/value', '/map2/value'),
        ('/map/sequence/0', '/map2/sequence/0'),
        ('/map/sequence/1', '/map2/sequence/1'),
        ('/map/sequence/0', '/seq2/0'),
        ('/map/sequence/1', '/seq2/1'),
        ('/map/value', '/val2'),
    ]
    for path1, path2 in equal_values:
        value1 = root.get_node_at_path(path1).value
        value2 = root.get_node_at_path(path2).value
        assert value1 == value2


def test_extract_node_properties():
    """Test extracting `TextValue` of node's tag and anchor."""
    doc = (
        "simple_tag: !tag 1\n"
        "tag_and_anchor: !tag &anchor 1\n"
        "anchor_and_tag: &anchor !tag 1\n"
        "multiline_tag_anchor:\n"
        "  !tag\n"
        "  &anchor\n"
        "  - 1"
    )
    loader = Loader()
    loader._document = doc

    loader._event = Mock(tag='tag', start_mark=Mock(line=0, column=12))
    tag = loader._extract_tag()
    assert tag.span.start.line == 1
    assert tag.span.start.column == 14
    assert tag.span.end.line == 1
    assert tag.span.end.column == 17

    loader._event = Mock(tag='tag', anchor='anchor',
                         start_mark=Mock(line=1, column=16))
    tag = loader._extract_tag()
    anchor = loader._extract_anchor()
    assert tag.span.start.line == 2
    assert tag.span.start.column == 18
    assert tag.span.end.line == 2
    assert tag.span.end.column == 21
    assert anchor.span.start.line == 2
    assert anchor.span.start.column == 23
    assert anchor.span.end.line == 2
    assert anchor.span.end.column == 29

    loader._event = Mock(tag='tag', anchor='anchor',
                         start_mark=Mock(line=2, column=16))
    tag = loader._extract_tag()
    anchor = loader._extract_anchor()
    assert tag.span.start.line == 3
    assert tag.span.start.column == 26
    assert tag.span.end.line == 3
    assert tag.span.end.column == 29
    assert anchor.span.start.line == 3
    assert anchor.span.start.column == 18
    assert anchor.span.end.line == 3
    assert anchor.span.end.column == 24

    loader._event = Mock(tag='tag', anchor='anchor',
                         start_mark=Mock(line=3, column=20))
    tag = loader._extract_tag()
    anchor = loader._extract_anchor()
    assert tag.span.start.line == 5
    assert tag.span.start.column == 4
    assert tag.span.end.line == 5
    assert tag.span.end.column == 7
    assert anchor.span.start.line == 6
    assert anchor.span.start.column == 4
    assert anchor.span.end.line == 6
    assert anchor.span.end.column == 10


def test_alias_errors():
    """Tests invalid aliases."""
    document = (
        "- &r text\n"
        "- *x\n"
        "- *r\n"
        "- *y"
    )
    loader = Loader()
    loader.load(document)
    assert len(loader.error_handler.errors) == 2


def test_merge():
    """Tests merge operator."""
    # taken from spec: http://yaml.org/type/merge.html
    document = (
        "anchors:\n"
        "  - &CENTER { x: 1, y: 2 }\n"
        "  - &LEFT { x: 0, y: 2 }\n"
        "  - &BIG { r: 10 }\n"
        "  - &SMALL { r: 1 }\n"
        "maps:\n"
        "  - # Merge one map\n"
        "    << : *CENTER\n"
        "    r: 10\n"
        "  - # Merge multiple maps\n"
        "    << : [ *CENTER, *BIG ]\n"
        "  - # Override\n"
        "    << : [ *BIG, *LEFT, *SMALL ]\n"
        "    x: 1\n"
    )
    loader = Loader()
    root = loader.load(document)

    assert root.get_node_at_path('/maps/0/x').value == 1
    assert root.get_node_at_path('/maps/0/y').value == 2
    assert root.get_node_at_path('/maps/0/r').value == 10
    assert root.get_node_at_path('/maps/1/x').value == 1
    assert root.get_node_at_path('/maps/1/y').value == 2
    assert root.get_node_at_path('/maps/1/r').value == 10
    assert root.get_node_at_path('/maps/2/x').value == 1
    assert root.get_node_at_path('/maps/2/y').value == 2
    assert root.get_node_at_path('/maps/2/r').value == 10

