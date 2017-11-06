"""Widget for picking a keyboard shortcut.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class KeyboardShortcutPicker(QPushButton):
    """Interactive button to display and configure keyboard shortcut."""

    STYLESHEET = """
    QPushButton {
        background-color: #bbb;
        border-style: outset;
        border-width: 1px;
        border-color: #444;
        padding: 5px 10px;
    }
    QPushButton:flat {
        background-color: #eee;
        border-color: blue;
    }
    """

    KEY_TRANSLATIONS = {
        Qt.Key_Control: 'Ctrl',
        Qt.Key_Shift: 'Shift',
        Qt.Key_Alt: 'Alt',
        Qt.Key_Backspace: 'Backspace',
        Qt.Key_Space: 'Space',
        Qt.Key_Insert: 'Insert',
        Qt.Key_Delete: 'Delete',
        Qt.Key_Tab: 'Tab',
        Qt.Key_Tab+1: 'Tab',
        Qt.Key_F1: 'F1',
        Qt.Key_F2: 'F2',
        Qt.Key_F3: 'F3',
        Qt.Key_F4: 'F4',
        Qt.Key_F5: 'F5',
        Qt.Key_F6: 'F6',
        Qt.Key_F7: 'F7',
        Qt.Key_F8: 'F8',
        Qt.Key_F9: 'F9',
        Qt.Key_F10: 'F10',
        Qt.Key_F11: 'F11',
        Qt.Key_F12: 'F12',
        Qt.Key_Home: 'Home',
        Qt.Key_End: 'End',
        Qt.Key_PageUp: 'PageUp',
        Qt.Key_PageDown: 'PageDown',
        Qt.Key_Left: 'Left',
        Qt.Key_Right: 'Right',
        Qt.Key_Up: 'Up',
        Qt.Key_Down: 'Down',
    }

    def __init__(self, shortcut, parent):
        super(KeyboardShortcutPicker, self).__init__(parent)
        self._shortcut = ''
        self.shortcut = shortcut
        self._editing = False
        self.new_combination = []
        self.clicked.connect(self.on_click)
        self.setText(shortcut)
        self.setStyleSheet(KeyboardShortcutPicker.STYLESHEET)
        self.setMinimumWidth(120)
        self.setFocusPolicy(Qt.NoFocus)

    @property
    def shortcut(self):
        """string representation of keyboard shortcut"""
        return self._shortcut

    @shortcut.setter
    def shortcut(self, value):
        """set shortcut"""
        self._shortcut = value
        self.setText(value)

    @property
    def editing(self):
        """whether keyboard shortcut is being edited"""
        return self._editing

    @editing.setter
    def editing(self, value):
        """set whether keyboard shortcut is being edited"""
        if not self._editing and value:
            # enter edit mode
            self._editing = True
            self.new_combination = []
            self.setFlat(self._editing)
        elif self._editing and not value:
            # exit edit mode
            self._editing = False
            self.setText(self.shortcut)
            self.setFlat(self._editing)

    def on_click(self, event):
        """Change editing state on mouse click."""
        self.editing = not self.editing
        self.setFocus()

    def keyPressEvent(self, event):
        """Create new shortcut from key presses if editing is active."""
        if not self.editing or event.type() != QtCore.QEvent.KeyPress:
            return

        key = event.key()

        if key in KeyboardShortcutPicker.KEY_TRANSLATIONS:
            key_label = KeyboardShortcutPicker.KEY_TRANSLATIONS[key]
        else:
            key_label = chr(key)

        # enable only modifiers as the first keys
        if len(self.new_combination) > 0 or key_label in ['Ctrl', 'Alt', 'Shift']:
            self.new_combination.append(key_label)
        else:
            return

        if self.is_valid_key_combination(self.new_combination):
            self.editing = False
            self.shortcut = '+'.join(self.new_combination)
        else:
            text = '+'.join(self.new_combination) + '+'
            self.setText(text)

    def keyReleaseEvent(self, event):
        """Exit editing mode if all keys are released."""
        if event.modifiers() == Qt.NoModifier:
            self.editing = False

    def focusOutEvent(self, event):
        """Exit editing mode when focus is lost."""
        self.editing = False

    @staticmethod
    def is_valid_key_combination(combination):
        """Determine if key combination is valid.

        :param list combination: list of key labels
        :return: True is combination is accepted
        :rtype: bool
        """
        return combination[-1] not in ['Ctrl', 'Alt', 'Shift']


if __name__ == '__main__':
    def main():
        """"Launches widget."""
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        picker = KeyboardShortcutPicker('Ctrl+C', None)
        picker.show()
        sys.exit(app.exec_())
    main()
