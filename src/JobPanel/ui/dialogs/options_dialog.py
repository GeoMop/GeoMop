"""Options dialog for Settings menu.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QComboBox)

from geomop_widgets import WorkspaceSelectorWidget
from geomop_analysis import Analysis


class OptionsDialog(QDialog):
    """Dialog containing settings."""

    MINIMUM_WIDTH = 320
    """minimum width of the dialog"""

    MINIMUM_HEIGHT = 300
    """minimum height of the dialog"""
    
    ENV_LABEL = "Local environment:"

    def __init__(self, parent, data, env, title='Options'):
        """Initializes the class."""
        super(OptionsDialog, self).__init__(parent)

        self.data = data
        self.workspace_selector = WorkspaceSelectorWidget(self, data.workspaces.get_path())
        
        self.envPresetLabel = QLabel(self.ENV_LABEL)
        self.envPresetComboBox = QComboBox()
        i = 0
        for key in env:
            self.envPresetComboBox.addItem(env[key].name, key)
        if data.config.local_env is not None:
            self.envPresetComboBox.setCurrentIndex(
                self.envPresetComboBox.findData(data.config.local_env))
        else:
            self.envPresetComboBox.setCurrentIndex(-1)
                


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)       
        

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.workspace_selector)        
        main_layout.addWidget(self.envPresetLabel)
        main_layout.addWidget(self.envPresetComboBox)
        main_layout.addStretch(1)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle(title)
        self.setMinimumSize(OptionsDialog.MINIMUM_WIDTH, OptionsDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        self.data.reload_workspace(self.workspace_selector.value)
        if not Analysis.exists(self.data.workspaces.get_path(), self.data.config.analysis):
            self.data.config.analysis = None
        self.data.config.local_env = self.envPresetComboBox.currentData()
        self.data.config.save()
        super(OptionsDialog, self).accept()       

