"""
Tests for YamlEditor
"""
__author__ = 'Tomas Krizek'


from ui.panels.yaml_editor import YamlEditorWidget


def test_insert_at_cursor_single():
    """Test `insert_at_cursor` method."""
    editor = YamlEditorWidget()
    text = 'abc'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insert_at_cursor(text)
    assert (2, 5) == editor.getCursorPosition()


def test_insert_at_cursor_multi():
    """Test `insert_at_cursor` method."""
    editor = YamlEditorWidget()
    text = 'abc\nqwerty'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insert_at_cursor(text)
    assert (3, 6) == editor.getCursorPosition()
