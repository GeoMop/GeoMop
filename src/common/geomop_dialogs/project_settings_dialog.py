"""Settings dialog.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout, QLabel, QComboBox)


class ProjectSettingsDialog(QDialog):
    """Dialog containing settings."""

    MINIMUM_WIDTH = 320
    """minimum width of the dialog"""

    MINIMUM_HEIGHT = 200
    """minimum height of the dialog"""

    def __init__(self, parent, project, flow123d_versions=None):
        """Initializes the class."""
        super(ProjectSettingsDialog, self).__init__(parent)

        self.project = project

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout = QFormLayout()
        f123d_version_label = QLabel("Flow123d version: ")
        self.f123d_version_combo_box = QComboBox()
        if flow123d_versions is None:
            flow123d_versions = [project.flow123d_version]
        self.f123d_version_combo_box.addItems(sorted(flow123d_versions, reverse=True))
        index = self.f123d_version_combo_box.findText(project.flow123d_version)
        index = 0 if index == -1 else index
        self.f123d_version_combo_box.setCurrentIndex(index)
        form_layout.addRow(f123d_version_label, self.f123d_version_combo_box)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle('Project Settings')
        self.setMinimumSize(ProjectSettingsDialog.MINIMUM_WIDTH, ProjectSettingsDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        self.project.flow123d_version = self.f123d_version_combo_box.currentText()
        self.project.save()
        super(ProjectSettingsDialog, self).accept()
