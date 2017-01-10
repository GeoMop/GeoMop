from PyQt5.QtWidgets import QMenu, QAction

class EditMenu(QMenu):
    """Menu with file actions."""

    def __init__(self, parent, diagram, title='&Edit'):
        """Initializes the class."""
        super(EditMenu, self).__init__(parent)
        self.setTitle(title)
        self._diagram = diagram
        self.parent = parent

        self._delete_action = QAction('&Delete', self)
        self._delete_action.setStatusTip('Delete selected items')
        self._delete_action.triggered.connect(self._delete)
        self.addAction(self._delete_action)
        
        self._deselect_action = QAction('Deselect &All', self)
        self._deselect_action.setStatusTip('Deselect selected items')
        self._deselect_action.triggered.connect(self._deselect)
        self.addAction(self._deselect_action)
        
        self._select_action = QAction('&Select All', self)
        self._select_action.setStatusTip('Select all items')
        self._select_action.triggered.connect(self._select)
        self.addAction(self._select_action)

    def _delete(self):
        """delete selected items"""
        self._diagram.delete_selected() 
 
    def _deselect(self):
        """deselect selected items"""
        self._diagram.deselect_selected() 
        
    def _select(self):
        """select all items"""
        self._diagram.select_all() 
