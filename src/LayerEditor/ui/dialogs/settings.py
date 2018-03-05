"""Settings dialog.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QWidget, QMessageBox,
                             QTabWidget, QCheckBox, QFormLayout, QLabel, QPushButton, QHBoxLayout,
                             QGroupBox, QComboBox)

from LayerEditor.helpers import keyboard_shortcuts_definition as shortcuts_definition
from LayerEditor.leconfig import cfg
from geomop_shortcuts import KeyboardShortcutPicker
from geomop_widgets import WorkspaceSelectorWidget


class SettingsDialog(QDialog):
    """Dialog containing settings."""

    MINIMUM_WIDTH = 320
    """minimum width of the dialog"""

    MINIMUM_HEIGHT = 300
    """minimum height of the dialog"""

    def __init__(self, parent, title='Settings'):
        """Initializes the class."""
        super(SettingsDialog, self).__init__(parent)

        tab_widget = QTabWidget()
        self.general_tab = GeneralTab(self)
        self.keyboard_shortcuts_tab = KeyboardShortcutsTab(self)
        tab_widget.addTab(self.general_tab, "General")
        tab_widget.addTab(self.keyboard_shortcuts_tab, "Keyboard Shortcuts")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle(title)
        self.setMinimumSize(SettingsDialog.MINIMUM_WIDTH, SettingsDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        cfg.config.workspace = self.general_tab.workspace_selector.value
        cfg.config.shortcuts = self.keyboard_shortcuts_tab.get_shortcuts()
        cfg.config.save()
        super(SettingsDialog, self).accept()


class GeneralTab(QWidget):
    """Tab containing common settings."""
    def __init__(self, parent=None):
        super(GeneralTab, self).__init__(parent)

        self.workspace_selector = WorkspaceSelectorWidget(self, cfg.config.workspace)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.workspace_selector)
        main_layout.addStretch(1)
        self.setLayout(main_layout)


class KeyboardShortcutsTab(QWidget):
    """Tab containing keyboard shortcuts."""
    def __init__(self, parent=None):
        super(KeyboardShortcutsTab, self).__init__(parent)

        main_layout = QVBoxLayout()
        label = QLabel("Changing Keyboard Shortcuts requires application restart.")
        label.setStyleSheet("color: red;")
        main_layout.addWidget(label)
        self.shortcuts_layout = None
        self.shortcuts_widgets = None
        self.init_keyboard_shortcuts_layout()
        main_layout.addLayout(self.shortcuts_layout)
        restore_defaults_button = QPushButton("Restore Defaults")
        restore_defaults_button.clicked.connect(self.restore_defaults)
        main_layout.addWidget(restore_defaults_button)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def init_keyboard_shortcuts_layout(self):
        """Initialize keyboard shortcuts layout with the user configured shortcuts."""
        self.shortcuts_layout = QFormLayout()
        self.shortcuts_widgets = {}

        for name, label in sorted(shortcuts_definition.SHORTCUT_LABELS.items(), key=lambda t: t[1]):
            shortcut = cfg.config.shortcuts[name]
            widget = KeyboardShortcutPicker(shortcut, self)
            self.shortcuts_widgets[name] = widget
            self.shortcuts_layout.addRow(label, widget)

    def get_shortcuts(self):
        """Get a dictionary of selected shortcuts.

        :return: dictionary of shortcut names and their string keyboard shortcut
        :rtype: dict
        """
        return {name: widget.shortcut for name, widget in self.shortcuts_widgets.items()}

    def restore_defaults(self):
        """Restore default keyboard shortcuts."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Restore Default Keyboard Shortcuts")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setText("Restore all keyboard shortcuts to their default settings?")

        if msg_box.exec_() == QMessageBox.Yes:
            for name, widget in self.shortcuts_widgets.items():
                widget.shortcut = shortcuts_definition.DEFAULT_USER_SHORTCUTS[name]


if __name__ == '__main__':
    def main():
        """"Launches widget."""
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        dialog = SettingsDialog(None)
        dialog.show()
        sys.exit(app.exec_())
    main()
