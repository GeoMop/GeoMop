"""Keyboard shortcuts helper.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from functools import lru_cache

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
        'SPACE': ord(' '),
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
        'SPACE': Qt.Key_Space,
    }

    __SHORTCUTS = {}

    def __init__(self, shortcut):
        """Initialize the class.

        :param str shortcut: string representation of a shortcut, use :samp:`+` to
           add modifiers
        """
        self.shortcut = shortcut
        self.key_sequence = QKeySequence(shortcut)
        self.qt_key = self._get_qt_code()
        self.scintilla_code = self._get_scintilla_code()
        # self.qt_modifiers = self._get_qt_modifiers()

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

    @property
    @lru_cache()
    def qt_modifiers(self):
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

    @staticmethod
    def get_shortcut(shortcut):
        """Return KeyboardShortcut from cache for this shortcut string.

        :param str shortcut: string of the shortcut
        :return: keyboard shortcut
        :rtype: KeyboardShortcut
        """
        if shortcut not in KeyboardShortcut.__SHORTCUTS:
            KeyboardShortcut.__SHORTCUTS[shortcut] = KeyboardShortcut(shortcut)
        return KeyboardShortcut.__SHORTCUTS[shortcut]


get_shortcut = KeyboardShortcut.get_shortcut


DEFAULT_USER_SHORTCUTS = {
    # editor actions
    'copy': 'Ctrl+C',
    'paste': 'Ctrl+V',
    'cut': 'Ctrl+X',
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Y',
    'indent': 'Tab',
    'unindent': 'Shift+Tab',
    'comment': 'Ctrl+/',
    'delete': 'Delete',
    'select_all': 'Ctrl+A',
    'show_autocompletion': 'Ctrl+Space',

    # menu actions
    'new_file': 'Ctrl+N',
    'open_file': 'Ctrl+O',
    'save_file': 'Ctrl+S',
    'save_file_as': 'Ctrl+Shift+S',
    'import_file': 'Ctrl+I',
    'exit': 'Ctrl+Q',
    'find': 'Ctrl+F',
    'replace': 'Ctrl+H',
    'edit_format': 'Ctrl+E',
}
"""default keyboard shortcuts"""


SHORTCUT_LABELS = {
    # editor actions
    'copy': 'Copy to clipboard',
    'paste': 'Paste from clipboard',
    'cut': 'Cut to clipboard',
    'undo': 'Undo an action',
    'redo': 'Redo an action',
    'indent': 'Increase indentation level',
    'unindent': 'Decrease indetation level',
    'comment': 'Toggle comment',
    'delete': 'Delete',
    'select_all': 'Select the entire text',
    'show_autocompletion': 'Display autocompletion options',

    # menu actions
    'new_file': 'New file',
    'open_file': 'Open file',
    'save_file': 'Save file',
    'save_file_as': 'Save file as',
    'import_file': 'Import file',
    'exit': 'Quit application',
    'find': 'Find dialog',
    'replace': 'Replace dialog',
    'edit_format': 'Edit format file',
}
"""labels of shortcuts to be displayed in the user interface"""


SYSTEM_SHORTCUTS = {
    'tab': 'Tab',
    'backspace': 'Backspace',
}
"""system keyboard shortcuts that can not be changed by user"""


SCINTILLA_DISABLE = [
    'copy',
    'paste',
    'cut',
    'undo',
    'redo',
    'indent',
    'unindent',
    'comment',
    'delete',
    'select_all',
    'show_autocompletion',
]
"""shortcuts to be disabled in default scintilla behavior"""
