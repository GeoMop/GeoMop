"""
Tests for YamlEditor
"""
__author__ = 'Tomas Krizek'


from panels.yaml_editor import YamlEditorWidget


def test_insertAtCursor_single_line():
    """Test `insertAtCursor` method."""
    editor = YamlEditorWidget()
    text = 'abc'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insertAtCursor(text)
    assert (2, 5) == editor.getCursorPosition()


def test_insertAtCursor_multi_line():
    """Test `insertAtCursor` method."""
    editor = YamlEditorWidget()
    text = 'abc\nqwerty'
    editor.setText("\n\ntest\n")
    editor.setCursorPosition(2, 2)
    editor.insertAtCursor(text)
    assert (3, 6) == editor.getCursorPosition()
