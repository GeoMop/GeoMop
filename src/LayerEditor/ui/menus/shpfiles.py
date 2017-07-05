from PyQt5.QtWidgets import QMenu, QAction

class ShpFilesMenu(QMenu):
    """Menu with shape file panel context actions."""

    def __init__(self, parent, shape_file_panel, file_idx):
        """Initializes the class."""
        super(ShpFilesMenu, self).__init__(parent)
        self.file_idx = file_idx
        
        self._remove_action = QAction('Remove', self)
        self._remove_action.setStatusTip('Remove shape file context')
        self._remove_action.triggered.connect(lambda: shape_file_panel.remove(self.file_idx))
        self.addAction(self._remove_action)
