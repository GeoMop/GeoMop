"""Tests for YamlEditor

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from ModelEditor.ui.panels.yaml_editor import YamlEditorWidget


def test_insert_at_cursor_single(qapp):
    """Test `insert_at_cursor` method."""
    editor = YamlEditorWidget()
    text = 'abc'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insert_at_cursor(text)
    assert (2, 5) == editor.getCursorPosition()


def test_insert_at_cursor_multi(qapp):
    """Test `insert_at_cursor` method."""
    editor = YamlEditorWidget()
    text = 'abc\nqwerty'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insert_at_cursor(text)
    assert (3, 6) == editor.getCursorPosition()
