import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtCore

from LayerEditor.data import cfg
from LayerEditor.ui.dialogs.diagram import DisplaySizeDlg


class EditMenu(QtWidgets.QMenu):
    """Menu with file actions."""

    def __init__(self, parent, title='&Edit'):
        """Initializes the class."""
        super(EditMenu, self).__init__(parent)
        self.setTitle(title)
        self.parent = parent
        
        self._undo_action = QtWidgets.QAction('&Undo', self)
        self._undo_action.setShortcut(cfg.get_shortcut('undo').key_sequence)
        self._undo_action.setStatusTip('Revert last operation')
        self._undo_action.triggered.connect(self.parent.undo)
        self.addAction(self._undo_action)
        
        self._redo_action = QtWidgets.QAction('&Redo', self)
        self._redo_action.setShortcut(cfg.get_shortcut('redo').key_sequence)
        self._redo_action.setStatusTip('Put last reverted operation back')
        self._redo_action.triggered.connect(self.parent.redo)
        self.addAction(self._redo_action)        

        self.addSeparator()
        
        self._init_area_action = QtWidgets.QAction('&Initialize Area', self)
        self._init_area_action.setCheckable(True)
        self._init_area_action.setChecked(cfg.init_area_visible)
        self._init_area_action.setStatusTip('Show initialization area')
        self.addAction(self._init_area_action)
        self._init_area_action.triggered.connect(self._show_init_area)
        
        self.addSeparator()

        self._delete_action = QtWidgets.QAction('&Delete', self)
        self._delete_action.setShortcut(cfg.get_shortcut('delete').key_sequence)
        self._delete_action.setStatusTip('Delete selected items')
        self._delete_action.triggered.connect(self._delete)
        self.addAction(self._delete_action)
        
        self._deselect_action = QtWidgets.QAction('Deselect &All', self)
        self._deselect_action.setShortcut(cfg.get_shortcut('deselect_all').key_sequence)
        self._deselect_action.setStatusTip('Deselect selected items')
        self._deselect_action.triggered.connect(self._deselect)
        self.addAction(self._deselect_action)
        
        self._select_action = QtWidgets.QAction('&Select All', self)
        self._select_action.setShortcut(cfg.get_shortcut('select_all').key_sequence)
        self._select_action.setStatusTip('Select all items')
        self._select_action.triggered.connect(self._select)
        self.addAction(self._select_action)
        
        self.addSeparator()

        self._display_all_action = QtWidgets.QAction('Dis&play All', self)
        self._display_all_action.setShortcut(cfg.get_shortcut('display_all').key_sequence)
        self._display_all_action.setStatusTip('Display all shapes')
        self._display_all_action.triggered.connect(self._display_all)
        self.addAction(self._display_all_action)
        
        self._display_area_action = QtWidgets.QAction('Display A&rea', self)
        self._display_area_action.setShortcut(cfg.get_shortcut('display_area').key_sequence)
        self._display_area_action.setStatusTip('Display area shapes')
        self._display_area_action.triggered.connect(self._display_area)
        self.addAction(self._display_area_action)
        
        self._display_action = QtWidgets.QAction('Displa&y ...', self)
        self._display_action.setShortcut(cfg.get_shortcut('display').key_sequence)
        self._display_action.setStatusTip('Display set area')
        self._display_action.triggered.connect(self._display)
        self.addAction(self._display_action)

    def _delete(self):
        """delete selected items"""
        self.parent.diagram_view.scene().delete_selected()
 
    def _deselect(self):
        """deselect selected items"""
        self.parent._layer_editor.le_model.gui_block_selector.value.selection.deselect_all()
        
    def _select(self):
        """select all items"""
        self.parent._layer_editor.le_model.gui_block_selector.value.selection.select_all()
        
    def _show_init_area(self):
        """Show initialization area menu action"""
        state = self._init_area_action.isChecked()
        cfg.init_area_visible = state
        self.parent.diagram_view.set_show_init_area(state)

    def _display_all(self):
        """Display all shapes"""
        self.parent.diagram_view.display_all()
        
    def _display_area(self):
        """Display initialization area"""
        self.parent.diagram_view.display_area()
        
    def _display(self):
        """Display set area"""
        view = self.parent.diagram_view
        rect = view.mapToScene(view.viewport().geometry()).boundingRect()
        dlg = DisplaySizeDlg(rect)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            rect = dlg.get_rect()
            view.fitInView(rect, QtCore.Qt.KeepAspectRatio)


