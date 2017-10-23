"""Module contains file menu widget.
"""
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup, qApp

from leconfig import cfg
from geomop_dialogs import GMAboutDialog


class MainFileMenu(QMenu):
    """Menu with file actions."""

    def __init__(self, parent, layer_editor, title='&File'):
        """Initializes the class."""
        super(MainFileMenu, self).__init__(parent)
        self.setTitle(title)
        self._layer_editor = layer_editor
        self.parent = parent
        self._about_dialog = GMAboutDialog(parent, 'GeoMop LayerEditor')

        self._new_file_action = QAction('&New File ...', self)
        self._new_file_action.setStatusTip('New layer data file')
        self._new_file_action.triggered.connect(self._layer_editor.new_file)
        self.addAction(self._new_file_action)

        self._open_file_action = QAction('&Open File ...', self)
        self._open_file_action.setStatusTip('Open layer data file')
        self._open_file_action.triggered.connect(self._layer_editor.open_file)
        self.addAction(self._open_file_action)
        
        self._save_file_action = QAction('&Save File', self)
        self._save_file_action.setStatusTip('Save layer data file')
        self._save_file_action.triggered.connect(self._layer_editor.save_file)
        self.addAction(self._save_file_action)

        self._save_as_action = QAction('Save &As ...', self)
        self._save_as_action.setStatusTip('Save layer data file as')
        self._save_as_action.triggered.connect(self._layer_editor.save_as)
        self.addAction(self._save_as_action)

        self._recent_file_signal_connect = False
        self._recent = self.addMenu('Open &Recent Files')
        self._recent_group = QActionGroup(self, exclusive=True)

        self.addSeparator()

        self._import_file_action = QAction('&Add Shape File ...', self)
        self._import_file_action.setStatusTip('Add shape file')
        self._import_file_action.triggered.connect(self._layer_editor.add_shape_file)
        self.addAction(self._import_file_action)

        self.addSeparator()

        self._make_mesh_action = QAction('Make &mesh ...', self)
        self._make_mesh_action.setStatusTip('Make mesh')
        self._make_mesh_action.triggered.connect(self._layer_editor.make_mesh)
        self.addAction(self._make_mesh_action)

        self.addSeparator()

        self._about_action = QAction('About', self)
        self._about_action.triggered.connect(self._on_about_action_clicked)
        self.addAction(self._about_action)

        self.addSeparator()

        self._exit_action = QAction('E&xit', self)
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
        self._recent_group.triggered.connect(self._layer_editor.open_recent)
        self._recent_file_signal_connect = True

    def _on_about_action_clicked(self):
        """Displays about dialog."""
        if not self._about_dialog.isVisible():
            self._about_dialog.show()
