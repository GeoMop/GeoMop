"""Tests for LineAnalyzer.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import pytest

from helpers import LineAnalyzer


@pytest.mark.parametrize('line, expected', [
    ('#', True),
    ('# key: 1', True),
    (' # key: 1', True),
    ('#  # key: 1', True),
    ('\t\t \t# key: 1', True),
    ('', False),
    ('  a # key: 1', False),
    ('key: 1', False),
])
def test_begins_with_comment(line, expected):
    """Test :py:meth:`begins_with_comment`."""
    assert LineAnalyzer.begins_with_comment(line) == expected


@pytest.mark.parametrize('line, expected', [
    ('#', ''),
    ('# ', ''),
    ('# key: 1', 'key: 1'),
    ('#key: 1', 'key: 1'),
    ('  # key: 1', '  key: 1'),
    ('  #key: 1', '  key: 1'),
    ('  # key: 1 # another comment', '  key: 1 # another comment'),
    ('  key: 1', '  key: 1'),
])
def test_uncomment(line, expected):
    """Test if uncomment removes the leading comment symbol."""
    assert LineAnalyzer.uncomment(line) == expected


@pytest.mark.parametrize('line, expected', [
    ('#', None),
    ('  #', None),
    ('a', 1),
    ('a: 1 # comment', 1),
    ('  a: 1', 3),
    ('  -', 3),
    ('  - ', 3),
    ('  - a', 5),
])
def test_get_node_start(line, expected):
    assert LineAnalyzer.get_node_start(line) == expected


@pytest.mark.parametrize('line, expected', [
    ('key:', 'key:'),
    ('#', ''),
    ('# test', ''),
    ('  ## abc', '  '),
    ('abc # abc', 'abc'),
    ('text example # abc', 'text example'),
    ('abc #abc', 'abc'),
    ('abc#abc #test', 'abc#abc'),
    ('key: 3 #test', 'key: 3'),
    ('key: abc ## comment', 'key: abc'),
])
def test_strip_comment(line, expected):
    assert LineAnalyzer.strip_comment(line) == expected


@pytest.mark.parametrize('line, index, expected', [
    ('word', 2, ('word', 2)),
    ('key:   4', 3, ('key: ', 3)),
    ('  key:   value', 5, ('key: ', 3)),
    ('  key:   value', 2, ('key: ', 0)),
    ('  key:   value', 10, ('value', 1)),
    ('  key:   value', 6, (None, None)),
    ('  key: *anchor', 8, ('*anchor', 1)),
    ('  key: *anchor', 9, ('*anchor', 2)),
    ('  key: !tag', 11, ('!tag', 4)),
    ('  key: !tag', 8, ('!tag', 1)),
    ('', 3, (None, None)),
    ('# key: 3', 3, (None, None)),
    ('  key: 3 # comment', 3, ('key: ', 1)),
    ('problem', 0, ('problem', 0)),
])
def test_get_autocomplete_context(line, index, expected):
    assert LineAnalyzer.get_autocomplete_context(line, index) == expected


@pytest.mark.parametrize('line, expected', [
    ('', True),
    ('  ', True),
    ('\t', True),
    ('\t \t', True),
    ('a ', False),
    (' a', False),
])
def test_is_empty(line, expected):
    assert LineAnalyzer.is_empty(line) == expected


@pytest.mark.parametrize('line, expected', [
    ('', 0),
    (' ', 1),
    ('  ', 2),
    ('\t', 2),
    ('  \t', 4),
    ('a', 0),
    ('  a', 2),
    ('  -', 2),
    ('  - a', 2),
    ('\n', 0),
])
def test_get_indent(line, expected):
    assert LineAnalyzer.get_indent(line) == expected


@pytest.mark.parametrize('line, start_index, expected', [
    ('12', None, '12'),
    ('key: ', None, 'key: '),
    ('key: 3', None, 'key: '),
    ('  key: 3', 2, 'key: '),
    ('  key: 3', None, ''),
    ('  key: 3', 2, 'key: '),
    ('!tag  ', None, '!tag'),
    ('*link  ', None, '*link'),
])
def test_get_autocompletion_word(line, start_index, expected):
    assert LineAnalyzer.get_autocompletion_word(line, start_index) == expected
