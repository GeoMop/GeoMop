import PyQt5.QtWidgets as QtWidgets
from ui.helpers import CurrentView
from leconfig import cfg
from ui.dialogs.diagram import DisplaySizeDlg

class EditMenu(QtWidgets.QMenu):
    """Menu with file actions."""

    def __init__(self, parent, diagram, title='&Edit'):
        """Initializes the class."""
        super(EditMenu, self).__init__(parent)
        self.setTitle(title)
        self._diagram = diagram
        self.parent = parent
        
        self._undo_action = QtWidgets.QAction('&Undo', self)
        self._undo_action.setShortcut(cfg.get_shortcut('undo').key_sequence)
        self._undo_action.setStatusTip('Revert last operation')
        self._undo_action.triggered.connect(self._undo)
        self.addAction(self._undo_action)
        
        self._redo_action = QtWidgets.QAction('&Redo', self)
        self._redo_action.setShortcut(cfg.get_shortcut('redo').key_sequence)
        self._redo_action.setStatusTip('Put last reverted operation back')
        self._redo_action.triggered.connect(self._redo)
        self.addAction(self._redo_action)        

        self.addSeparator()
        
        self._init_area_action = QtWidgets.QAction('&Initialize Area', self)
        self._init_area_action.setCheckable(True)
        self._init_area_action.setChecked(cfg.config.show_init_area) 
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
        
    def _undo(self):
        """Revert last diagram operation"""
        self._deselect()

        view = cfg.history.get_undo_view()
        if view is not None:
            view.set_view()
        while True:
            ret, ops = cfg.history.try_undo_to_label() 
            if ops["type"] is not None:
                if ops["type"]=="Diagram":
                    self._diagram.update_changes(
                        ops["added_points"], ops["removed_points"], 
                        ops["moved_points"], ops["added_lines"], ops["removed_lines"])
                elif ops["type"]=="Layers":  
                    if ops["edit_first"]: 
                        CurrentView.set_view_id(0, cfg)
                    if ops["check_viewed"]: 
                        cfg.main_window.diagramScene.update_views()                                
                    if ops["refresh_panel"]: 
                        cfg.main_window.update_layers_panel()
                elif ops["type"]=="Regions":  
                    if ops["refresh_panel"]: 
                        cfg.main_window.set_topology()
            if ret:
                self._diagram._add_polygons()
                self._diagram._del_polygons()
                return
            view = cfg.history.get_undo_view()
            if view is not None:
                view.set_view()

    def _redo(self):
        """Put last diagram reverted operation back"""
        self._deselect()

        view = cfg.history.get_redo_view()
        if view is not None:
            view.set_view()
        
        while True:
            ret, ops = cfg.history.try_redo_to_label()             
            if ops["type"] is not None:
                if ops["type"]=="Diagram":
                    self._diagram.update_changes(
                        ops["added_points"], ops["removed_points"], 
                        ops["moved_points"], ops["added_lines"], ops["removed_lines"])
                elif ops["type"]=="Layers":
                    if ops["edit_first"]: 
                        CurrentView.set_view_id(0, cfg)                        
                    if ops["check_viewed"]: 
                        cfg.main_window.diagramScene.update_views()                                   
                    if ops["refresh_panel"]: 
                        cfg.main_window.update_layers_panel()
                elif ops["type"]=="Regions": 
                    if ops["refresh_panel"]: 
                        cfg.main_window.set_topology()
            if ret:
                self._diagram._add_polygons()
                self._diagram._del_polygons()
                return
            view = cfg.history.get_redo_view()
            if view is not None:
                view.set_view()

    def _delete(self):
        """delete selected items"""
        self._diagram.delete_selected() 
 
    def _deselect(self):
        """deselect selected items"""
        self._diagram.selection.deselect_selected()
        
    def _select(self):
        """select all items"""
        self._diagram.select_all()
        
    def _show_init_area(self):
        """Show initialization area menu action"""
        state = self._init_area_action.isChecked()
        cfg.config.show_init_area = state
        self._diagram.show_init_area(state)
        
    def _display_all(self):
        """Display all shapes"""
        cfg.main_window.display_all()
        
    def _display_area(self):
        """Display initialization area"""
        cfg.main_window.display_area()
        
    def _display(self):
        """Display set area"""
        rect = cfg.main_window.get_display_rect()
        dlg = DisplaySizeDlg(rect, cfg.main_window)
        ret = dlg.exec_()
        if ret==QtWidgets.QDialog.Accepted:
            rect = dlg.get_rect()
            cfg.main_window.display_rect(rect)
            
        
