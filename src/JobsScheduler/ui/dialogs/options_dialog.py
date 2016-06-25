"""Options dialog for Settings menu.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox)

from geomop_widgets import WorkspaceSelectorWidget
from geomop_analysis import Analysis


class OptionsDialog(QDialog):
    """Dialog containing settings."""

    MINIMUM_WIDTH = 320
    """minimum width of the dialog"""

    MINIMUM_HEIGHT = 300
    """minimum height of the dialog"""

    def __init__(self, parent, config, title='Options'):
        """Initializes the class."""
        super(OptionsDialog, self).__init__(parent)

        self.config = config
        self.workspace_selector = WorkspaceSelectorWidget(self, config.workspace)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.workspace_selector)
        main_layout.addStretch(1)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle(title)
        self.setMinimumSize(OptionsDialog.MINIMUM_WIDTH, OptionsDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        self.config.workspace = self.workspace_selector.value
        if not Analysis.exists(self.config.workspace, self.config.analysis):
            self.config.analysis = None
        self.config.save()
        super(OptionsDialog, self).accept()
