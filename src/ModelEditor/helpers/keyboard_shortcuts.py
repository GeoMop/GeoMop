"""
Keyboard shortcuts helper.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


class KeyboardShortcut:
    """Represents a keyboard shortcut."""

    # pylint: disable=too-few-public-methods

    __SCINTILLA_KEY_CODES = {
        'CTRL': QsciScintilla.SCMOD_CTRL << 16,
        'SHIFT': QsciScintilla.SCMOD_SHIFT << 16,
        'ALT': QsciScintilla.SCMOD_ALT << 16,
        'TAB': QsciScintilla.SCK_TAB,
        'DELETE': QsciScintilla.SCK_DELETE,
        'ENTER': QsciScintilla.SCK_RETURN,
        'ESC': QsciScintilla.SCK_ESCAPE,
        'BACKSPACE': QsciScintilla.SCK_BACK,
    }

    __QT_MODIFIERS = {
        'CTRL': Qt.ControlModifier,
        'SHIFT': Qt.ShiftModifier,
        'ALT': Qt.AltModifier,
    }

    __QT_KEYS = {
        'TAB': Qt.Key_Tab,
        'DELETE': Qt.Key_Delete,
        'ENTER': Qt.Key_Return,
        'ESC': Qt.Key_Escape,
        'BACKSPACE': Qt.Key_Backspace,
    }

    def __init__(self, shortcut):
        """Initialize the class.

        :param str shortcut: string representation of a shortcut, use :samp:`+` to
           add modifiers
        """
        self.shortcut = shortcut
        self.key_sequence = QKeySequence(shortcut)
        self.qt_key = self._get_qt_code()
        self.scintilla_code = self._get_scintilla_code()
        self.qt_modifiers = self._get_qt_modifiers()

    def _get_scintilla_code(self):
        """Return Scintilla key code."""
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
        """Return Qt KeyModifiers."""
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

    def matches_key_event(self, event):
        """Return True if this keyboard shortcut matches the key event.

        :param QKeyEvent event: event that occurred
        :return: True if this shortcut matches the event
        :rtype: bool
        """
        return event.modifiers() == self.qt_modifiers and event.key() == self.qt_key


COPY = KeyboardShortcut('Ctrl+C')
PASTE = KeyboardShortcut('Ctrl+V')
CUT = KeyboardShortcut('Ctrl+X')
UNDO = KeyboardShortcut('Ctrl+Z')
REDO = KeyboardShortcut('Ctrl+Y')
INDENT = KeyboardShortcut('Tab')  # TODO remove duplicate (Tab), better shortcuts system
UNINDENT = KeyboardShortcut('Shift+Tab')
COMMENT = KeyboardShortcut('Ctrl+/')
DELETE = KeyboardShortcut('Delete')
ENTER = KeyboardShortcut('Enter')
SELECT_ALL = KeyboardShortcut('Ctrl+A')
FIND = KeyboardShortcut('Ctrl+F')
REPLACE = KeyboardShortcut('Ctrl+H')
NEW_FILE = KeyboardShortcut('Ctrl+N')
OPEN_FILE = KeyboardShortcut('Ctrl+O')
SAVE_FILE = KeyboardShortcut('Ctrl+S')
SAVE_FILE_AS = KeyboardShortcut('Ctrl+Shift+S')
IMPORT_FILE = KeyboardShortcut('Ctrl+I')
EXIT = KeyboardShortcut('Ctrl+Q')
EDIT_FORMAT = KeyboardShortcut('Ctrl+E')
SHOW_AUTOCOMPLETE = KeyboardShortcut('Ctrl+ ')
ESCAPE = KeyboardShortcut('Esc')
BACKSPACE = KeyboardShortcut('Backspace')
TAB = KeyboardShortcut('Tab')

"""
shortcuts to be disabled in default scintilla behavior
"""
SCINTILLA_DISABLE = [
    COPY,
    PASTE,
    CUT,
    UNDO,
    REDO,
    INDENT,
    UNINDENT,
    COMMENT,
    DELETE,
    SELECT_ALL,
    SHOW_AUTOCOMPLETE,
]
