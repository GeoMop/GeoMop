"""Module contains settings menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup

#from leconfig import cfg
from ..dialogs.settings import SettingsDialog


class MainSettingsMenu(QMenu):
    """Menu with settings actions."""

    def __init__(self, parent, layer_editor, title='&Settings'):
        """Initializes the class."""
        super(MainSettingsMenu, self).__init__(parent)
        self.setTitle(title)
        self._layer_editor = layer_editor
        self.parent = parent

        self.options_action = QAction('&Options ...', self)
        self.options_action.setStatusTip('Configure editor options')
        self.options_action.triggered.connect(self.on_options_action)
        self.addAction(self.options_action)

    def on_options_action(self):
        """Handle options action - display settings."""
        dialog = SettingsDialog(self.parent)
        dialog.exec_()
