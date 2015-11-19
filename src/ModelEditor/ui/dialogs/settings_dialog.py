"""Settings dialog.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QWidget,
                             QTabWidget, QCheckBox)

from meconfig import cfg


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
        self.general_tab = GeneralTab()
        tab_widget.addTab(self.general_tab, "General")
        tab_widget.addTab(QWidget(), "Hotkeys")

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
        cfg.config.display_autocompletion = self.general_tab.autocompletion_checkbox.isChecked()
        cfg.config.save()
        super(SettingsDialog, self).accept()


class GeneralTab(QWidget):
    """Tab containing common settings."""
    def __init__(self, parent=None):
        super(GeneralTab, self).__init__(parent)

        self.autocompletion_checkbox = QCheckBox("Display Autocompletion (automatically)")
        if cfg.config.display_autocompletion:
            self.autocompletion_checkbox.setChecked(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.autocompletion_checkbox)
        main_layout.addStretch(1)
        self.setLayout(main_layout)


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
