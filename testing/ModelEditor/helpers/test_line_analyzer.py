"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from helpers import LineAnalyzer


def test_begins_with_comment():
    """Test :py:meth:`begins_with_comment`."""
    begins_with_comment = LineAnalyzer.begins_with_comment
    assert begins_with_comment('#') is True
    assert begins_with_comment('# key: 1') is True
    assert begins_with_comment(' # key: 1') is True
    assert begins_with_comment('#  # key: 1') is True
    assert begins_with_comment('\t\t \t# key: 1') is True
    assert begins_with_comment('') is False
    assert begins_with_comment('  a # key: 1') is False
    assert begins_with_comment('key: 1') is False


def test_uncomment():
    """Test if uncomment removes the leading comment symbol."""
    uncomment = LineAnalyzer.uncomment
    assert uncomment('#') == ''
    assert uncomment('# ') == ''
    assert uncomment('# key: 1') == 'key: 1'
    assert uncomment('#key: 1') == 'key: 1'
    assert uncomment('  # key: 1') == '  key: 1'
    assert uncomment('  #key: 1') == '  key: 1'
    assert uncomment('  # key: 1 # another comment') == '  key: 1 # another comment'


def test_get_node_start():
    get_node_start = LineAnalyzer.get_node_start
    assert get_node_start('#') is None
    assert get_node_start('  #') is None
    assert get_node_start('a') == 1
    assert get_node_start('a: 1 # comment') == 1
    assert get_node_start('  a: 1') == 3
    assert get_node_start('  -') == 3
    assert get_node_start('  - ') == 3
    assert get_node_start('  - a') == 5


def test_strip_comment():
    strip_comment = LineAnalyzer.strip_comment
    assert strip_comment('key:') == 'key:'
    assert strip_comment('#') == ''
    assert strip_comment('# test') == ''
    assert strip_comment('  ## abc') == '  '
    assert strip_comment('abc # abc') == 'abc'
    assert strip_comment('text example # abc') == 'text example'
    assert strip_comment('abc #abc') == 'abc'
    assert strip_comment('abc#abc #test') == 'abc#abc'
    assert strip_comment('key: 3 #test') == 'key: 3'
