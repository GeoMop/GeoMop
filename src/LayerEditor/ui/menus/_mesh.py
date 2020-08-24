from PyQt5.QtWidgets import QMenu, QAction


class MeshMenu(QMenu):
    """Menu with mesh actions."""

    def __init__(self, parent, layer_editor, title='&Mesh'):
        """Initializes the class."""
        super().__init__(parent)
        self.setTitle(title)
        self._layer_editor = layer_editor
        self.parent = parent

        self._make_mesh_action = QAction('&Make mesh ...', self)
        self._make_mesh_action.setStatusTip('Make mesh')
        self._make_mesh_action.triggered.connect(self._layer_editor.make_mesh)
        self.addAction(self._make_mesh_action)
