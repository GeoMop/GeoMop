"""Module contains settings menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup

from meconfig import cfg
from ui.dialogs import SettingsDialog, ChangeISTDialog
from ui.template import EditorAppearance


class MainSettingsMenu(QMenu):
    """Menu with settings actions."""

    def __init__(self, parent, model_editor, title='&Settings'):
        """Initializes the class."""
        super(MainSettingsMenu, self).__init__(parent)
        self.setTitle(title)
        self._model_editor = model_editor
        self.parent = parent

        self.format_action = QAction('&Change File Format ...', self)
        self.format_action.setStatusTip('Change file Flow123d version')
        self.format_action.triggered.connect(self.on_change_file_format)
        self.addAction(self.format_action)

        self._transformation = self.addMenu('&Transformation')
        pom_lamda = lambda name: lambda: self._model_editor.transform(name)
        for frm in cfg.transformation_files:
            faction = QAction(frm + " ...", self)
            faction.setStatusTip('Transform format of current document')
            self._transformation.addAction(faction)
            faction.triggered.connect(pom_lamda(frm))

        self.options_action = QAction('&Options ...', self)
        self.options_action.setStatusTip('Configure editor options')
        self.options_action.triggered.connect(self.on_options_action)
        self.addAction(self.options_action)

        if cfg.config.DEBUG_MODE:
            self._edit_transformation = self.addMenu('&Edit Transformation Rules')
            pom_lamda = lambda name: lambda: self._model_editor.edit_transformation_file(name)
            for frm in cfg.transformation_files:
                faction = QAction(frm, self)
                faction.setStatusTip('Open transformation file')
                self._edit_transformation.addAction(faction)
                faction.triggered.connect(pom_lamda(frm))

    def on_options_action(self):
        """Handle options action - display settings."""
        dialog = SettingsDialog(self.parent)
        if dialog.exec_():
            EditorAppearance.set_default_appearence(self._model_editor.mainwindow.editor)

    def on_change_file_format(self):
        """Handle change format action - display dialog."""
        dialog = ChangeISTDialog(self.parent)
        if dialog.exec_():
            cfg.update_format()
            cfg.main_window.reload()
