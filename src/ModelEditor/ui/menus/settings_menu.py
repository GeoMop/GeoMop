"""Module contains settings menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup

import helpers.keyboard_shortcuts as shortcuts
from meconfig import cfg
from ui.dialogs import SettingsDialog


class MainSettingsMenu(QMenu):
    """Menu with settings actions."""

    def __init__(self, parent, model_editor, title='&Settings'):
        """Initializes the class."""
        super(MainSettingsMenu, self).__init__(parent)
        self.setTitle(title)
        self._model_editor = model_editor
        self.parent = parent

        self._format = self.addMenu('&Format')
        self._format_group = QActionGroup(self, exclusive=True)
        for frm in cfg.format_files:
            faction = self._format_group.addAction(QAction(
                frm, self, checkable=True))
            faction.setStatusTip('Choose format file for current document')
            self._format.addAction(faction)
            faction.setChecked(cfg.curr_format_file == frm)
        self._format_group.triggered.connect(self._format_checked)

        self._format.addSeparator()

        if cfg.config.DEBUG_MODE:
            self._edit_format_action = QAction(
                '&Edit Format File ...', self)
            self._edit_format_action.setShortcut(shortcuts.EDIT_FORMAT.key_sequence)
            self._edit_format_action.setStatusTip('Edit format file in Json Editor')
            self._edit_format_action.triggered.connect(self._model_editor.edit_format)
            self._format.addAction(self._edit_format_action)

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

    def _format_checked(self):
        """Format checked action handler."""
        action = self._format_group.checkedAction()
        filename = action.text()
        self._model_editor.select_format(filename)

    def on_options_action(self):
        """Handle options action - display settings."""
        SettingsDialog(self.parent).exec_()
