"""Change IST dialog.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout, QLabel, QComboBox)
from meconfig import cfg


class ChangeISTDialog(QDialog):
    """Dialog containing settings."""

    MINIMUM_WIDTH = 320
    """minimum width of the dialog"""

    MINIMUM_HEIGHT = 200
    """minimum height of the dialog"""

    def __init__(self, parent):
        """Initializes the class."""
        super(ChangeISTDialog, self).__init__(parent)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout = QFormLayout()
        f123d_version_label = QLabel("Flow123d version: ")
        self.f123d_version_combo_box = QComboBox()
        self.f123d_version_combo_box.addItems(sorted(cfg.format_files, reverse=True))
        index = self.f123d_version_combo_box.findText(cfg.curr_format_file)
        index = 0 if index == -1 else index
        self.f123d_version_combo_box.setCurrentIndex(index)
        form_layout.addRow(f123d_version_label, self.f123d_version_combo_box)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle('Change Flow123d version')
        self.setMinimumSize(ChangeISTDialog.MINIMUM_WIDTH, ChangeISTDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        cfg.curr_format_file = self.f123d_version_combo_box.currentText()
        try:
            node = cfg.root.get_node_at_path('/flow123d_version')
        except LookupError:
            pass
        else:
            # replace text
            pass
        super(ChangeISTDialog, self).accept()
