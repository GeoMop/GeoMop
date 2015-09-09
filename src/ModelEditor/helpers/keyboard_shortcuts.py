"""
Keyboard shortcuts helper.
"""

__author__ = 'Tomas Krizek'

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


class KeyboardShortcut:
    """Represents a keyboard shortcut."""

    __SCINTILLA_KEY_CODES = {
        'CTRL': QsciScintilla.SCMOD_CTRL << 16,
        'SHIFT': QsciScintilla.SCMOD_SHIFT << 16,
        'ALT': QsciScintilla.SCMOD_ALT << 16,
        'TAB': QsciScintilla.SCK_TAB,
        'DELETE': QsciScintilla.SCK_DELETE,
    }

    __QT_MODIFIERS = {
        'CTRL': Qt.ControlModifier,
        'SHIFT': Qt.ShiftModifier,
        'ALT': Qt.AltModifier
    }

    __QT_KEYS = {
        'TAB': Qt.Key_Tab,
        'DELETE': Qt.Key_Delete,
    }

    def __init__(self, shortcut):
        """Initializes the class."""
        self.shortcut = shortcut
        self.key_sequence = QKeySequence(shortcut)
        self.qt_key = self._get_qt_code()
        self.scintilla_code = self._get_scintilla_code()
        self.qt_modifiers = self._get_qt_modifiers()

    def _get_scintilla_code(self):
        """Returns Scintilla key code."""
        code = 0
        for key in self.shortcut.split(',')[0].upper().split('+'):
            if key in KeyboardShortcut.__SCINTILLA_KEY_CODES:
                code += KeyboardShortcut.__SCINTILLA_KEY_CODES[key]
            else:
                try:
                    code += ord(key)
                except TypeError:
                    return None
        return code

    def _get_qt_modifiers(self):
        """Returns Qt KeyModifiers."""
        qt_modifiers = Qt.NoModifier
        for key in self.shortcut.split(',')[0].upper().split('+'):
            if key in KeyboardShortcut.__QT_MODIFIERS:
                qt_modifiers |= KeyboardShortcut.__QT_MODIFIERS[key]
        return qt_modifiers

    def _get_qt_code(self):
        """Return Qt key code."""
        for key in self.shortcut.split(',')[0].upper().split('+'):
            if key in KeyboardShortcut.__QT_KEYS:
                return KeyboardShortcut.__QT_KEYS[key]
            elif key in KeyboardShortcut.__QT_MODIFIERS:
                continue
            else:
                try:
                    return ord(key)
                except TypeError:
                    return None

    def matches_key_kvent(self, event):
        """Returns True if the keyboard shortcut matches given `QKeyEvent`."""
        return event.modifiers() == self.qt_modifiers and event.key() == self.qt_key


SCINTILLA = {
    'COPY': KeyboardShortcut('Ctrl+C'),
    'PASTE': KeyboardShortcut('Ctrl+V'),
    'CUT': KeyboardShortcut('Ctrl+X'),
    'UNDO': KeyboardShortcut('Ctrl+Z'),
    'REDO': KeyboardShortcut('Ctrl+Y'),
    'INDENT': KeyboardShortcut('Tab'),
    'UNINDENT': KeyboardShortcut('Shift+Tab'),
    'COMMENT': KeyboardShortcut('Ctrl+/'),
    'DELETE': KeyboardShortcut('Delete'),
    'SELECT_ALL': KeyboardShortcut('Ctrl+A'),
    'FIND': KeyboardShortcut('Ctrl+F'),
    'REPLACE': KeyboardShortcut('Ctrl+H'),
}
