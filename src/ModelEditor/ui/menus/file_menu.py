"""Module contains file menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup, qApp

from meconfig import cfg
from geomop_dialogs import GMAboutDialog


class MainFileMenu(QMenu):
    """Menu with file actions."""

    def __init__(self, parent, model_editor, title='&File'):
        """Initializes the class."""
        super(MainFileMenu, self).__init__(parent)
        self.setTitle(title)
        self._model_editor = model_editor
        self.parent = parent
        self._about_dialog = GMAboutDialog(self._model_editor.mainwindow, 'GeoMop ModelEditor')

        self._new_file_action = QAction('&New File ...', self)
        self._new_file_action.setShortcut(cfg.get_shortcut('new_file').key_sequence)
        self._new_file_action.setStatusTip('New model yaml file')
        self._new_file_action.triggered.connect(self._model_editor.new_file)
        self.addAction(self._new_file_action)

        self._open_file_action = QAction('&Open File ...', self)
        self._open_file_action.setShortcut(cfg.get_shortcut('open_file').key_sequence)
        self._open_file_action.setStatusTip('Open model yaml file')
        self._open_file_action.triggered.connect(self._model_editor.open_file)
        self.addAction(self._open_file_action)

        self._save_file_action = QAction('&Save File', self)
        self._save_file_action.setShortcut(cfg.get_shortcut('save_file').key_sequence)
        self._save_file_action.setStatusTip('Save model yaml file')
        self._save_file_action.triggered.connect(self._model_editor.save_file)
        self.addAction(self._save_file_action)

        self._save_as_action = QAction('Save &As ...', self)
        self._save_as_action.setShortcut(cfg.get_shortcut('save_file_as').key_sequence)
        self._save_as_action.setStatusTip('Save model yaml file as')
        self._save_as_action.triggered.connect(self._model_editor.save_as)
        self.addAction(self._save_as_action)

        self._recent_file_signal_connect = False
        self._recent = self.addMenu('Open &Recent Files')
        self._recent_group = QActionGroup(self, exclusive=True)

        self.addSeparator()

        self._import_file_action = QAction('&Import File ...', self)
        self._import_file_action.setShortcut(cfg.get_shortcut('import_file').key_sequence)
        self._import_file_action.setStatusTip('Import model from old con formatted file')
        self._import_file_action.triggered.connect(self._model_editor.import_file)
        self.addAction(self._import_file_action)

        self.addSeparator()

        self._about_action = QAction('About', self)
        self._about_action.triggered.connect(self._on_about_action_clicked)
        self.addAction(self._about_action)

        self.addSeparator()

        self._exit_action = QAction('E&xit', self)
        self._exit_action.setShortcut(cfg.get_shortcut('exit').key_sequence)
        self._exit_action.setStatusTip('Exit application')
        self._exit_action.triggered.connect(qApp.quit)
        self.addAction(self._exit_action)

    def update_recent_files(self, from_row=1):
        """update recent file in menu"""
        if self._recent_file_signal_connect:
            self._recent_group.triggered.disconnect()
            self._recent_file_signal_connect = False
        for action in self._recent_group.actions():
            self._recent_group.removeAction(action)
        if len(cfg.config.recent_files) < from_row+1:
            self._recent.setEnabled(False)
            return
        self._recent.setEnabled(True)
        for i in range(from_row, len(cfg.config.recent_files)):
            reaction = self._recent_group.addAction(QAction(
                cfg.config.recent_files[i], self, checkable=True))
            self._recent.addAction(reaction)
        self._recent_group.triggered.connect(self._model_editor.open_recent)
        self._recent_file_signal_connect = True

    def _on_about_action_clicked(self):
        """Displays about dialog."""
        if not self._about_dialog.isVisible():
            self._about_dialog.show()
