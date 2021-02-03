"""Main Qt window.
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from LayerEditor.ui.layers_panel.layers_panel import LayerPanel
from LayerEditor.ui.panels.regions_panel import RegionsPanel
from LayerEditor.ui.tools.cursor import Cursor
from LayerEditor.ui.diagram_editor.diagram_view import DiagramView
import gm_base.icon as icon
from LayerEditor.ui.menus.file import MainFileMenu
from LayerEditor.ui.tools import undo


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, layer_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()
        self._layer_editor = layer_editor
        self.make_widgets(True)

    @property
    def curr_scene(self):
        return self.diagram_view.scene()

    def make_widgets(self, first=False):
        self.wg_regions_panel = RegionsPanel(self._layer_editor.le_model, self)

        self.setMinimumSize(1060, 660)

        Cursor.setup_cursors()

        # splitters
        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.setCentralWidget(self._hsplitter)

        # left pannels
        self._vsplitter1 = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self._vsplitter1.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.scroll_area1 = QtWidgets.QScrollArea()
        # self._scroll_area.setWidgetResizable(True)
        self.layers = LayerPanel(self._layer_editor.le_model)
        self._vsplitter1.addWidget(self.layers)

        self._vsplitter1.addWidget(self.wg_regions_panel)

        # scene
        self.diagram_view = DiagramView(self._layer_editor.le_model)
        """View is common for all layers and blocks."""
        self._layer_editor.le_model.scenes_changed.connect(self.diagram_view.scenes_changed)
        self._layer_editor.le_model.active_block_changed.connect(self.change_curr_block)

        self._hsplitter.addWidget(self.diagram_view)

        self._hsplitter.setSizes([300, 760])

        # right pannels
        self._vsplitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self._vsplitter2.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.scroll_area2 = QtWidgets.QScrollArea()
        self.scroll_area2.setWidgetResizable(True)
        #self.wg_surface_panel = panels.Surfaces(cfg.layers, cfg.config.data_dir, parent=self.scroll_area2)
        #self.scroll_area2.setWidget(self.wg_surface_panel)
        self._vsplitter2.addWidget(self.scroll_area2)

        #self.shp = panels.ShpFiles(cfg.diagram.shp, self._vsplitter2)
        #self._vsplitter2.addWidget(self.shp)
        #if cfg.diagram.shp.is_empty():
        #    self.shp.hide()

        # if not cfg.diagram.shp.is_empty():
        #     self.refresh_diagram_shp()

        # Menu bar
        self._menu = self.menuBar()
        # self._edit_menu = EditMenu(self, self.diagramScene)
        self._file_menu = MainFileMenu(self, self._layer_editor)
        # self._analysis_menu = AnalysisMenu(self, cfg.config)
        # self._settings_menu = MainSettingsMenu(self, self._layer_editor)
        # self._mesh_menu = MeshMenu(self, self._layer_editor)
        self.update_recent_files(0)
        if first:
            self._menu.addMenu(self._file_menu)
            # self._menu.addMenu(self._edit_menu)
            # self._menu.addMenu(self._analysis_menu)
            # self._menu.addMenu(self._settings_menu)
            # self._menu.addMenu(self._mesh_menu)

        # status bar
        self._column = QtWidgets.QLabel(self)
        self._column.setFrameStyle(QtWidgets.QFrame.StyledPanel)

        self._reload_icon = QtWidgets.QLabel(self)
        self._reload_icon.setPixmap(icon.get_pixmap("refresh", 16))
        self._reload_icon.setVisible(False)
        self._reload_icon_timer = QtCore.QTimer(self)
        self._reload_icon_timer.timeout.connect(lambda: self._reload_icon.setVisible(False))

        self._analysis_label = QtWidgets.QLabel(self)
        # cfg.config.observers.append(self)

        self._status = QtWidgets.QStatusBar()
        self._status.addPermanentWidget(self._reload_icon)
        self._status.addPermanentWidget(self._analysis_label)
        self._status.addPermanentWidget(self._column)
        self.setStatusBar(self._status)
        self._status.showMessage("Ready", 5000)

        # signals
        self.diagram_view.cursorChanged.connect(self._cursor_changed)
        # self.shp.background_changed.connect(self.background_changed)
        # self.shp.item_removed.connect(self.del_background_item)
        # self.layers.viewInterfacesChanged.connect(self.refresh_view_data)
        # self.layers.editInterfaceChanged.connect(self.refresh_curr_data)
        # self.layers.topologyChanged.connect(self.set_topology)
        # self.layers.refreshArea.connect(self._refresh_area)
        # self.layers.clearDiagramSelection.connect(self.clear_diagram_selection)

        self._layer_editor.le_model.invalidate_scene.connect(self.update_scene)
        self._layer_editor.le_model._layers_changed.connect(self.layers_changed)

        # self.wg_surface_panel.show_grid.connect(self._show_grid)

    def update_recent_files(self, from_row=1):
        """Update recently opened files."""
        self._file_menu.update_recent_files(from_row)

    # def refresh_diagram_shp(self):
    #     """refresh diagrams shape files background layer"""
    #     self.diagramScene.refresh_shp_backgrounds()
    #     if not cfg.diagram.shp.is_empty():
    #         if not self.shp.isVisible():
    #             self.shp.show()
    #         self.shp.reload()
    #     else:
    #         self.shp.hide()
    #
    #     if cfg.diagram.first_shp_object():
    #         self.display_all()
    #     else:
    #         self._move()
    #
    def _cursor_changed(self, x, y):
        """Editor node change signal"""
        self._column.setText("x: {:5f}  y: {:5f}".format(x, -y))

    def layers_changed(self):
        self.update_all()

    def update_scene(self):
        self.curr_scene.update_scene()

    # def _show_grid(self, show_flag):
    #     """Show mash"""
    #     if show_flag:
    #         quad, nuv = self.wg_surface_panel.get_curr_quad()
    #         if quad is None:
    #             return
    #         rect = self.diagramScene.show_grid(quad, nuv)
    #         view_rect = self.diagramView.sceneRect()
    #         if not view_rect.contains(rect):
    #             view_rect = view_rect.united(rect)
    #             self.display_rect(view_rect)
    #     else:
    #         self.diagramScene.hide_grid()

    def closeEvent(self, event):
        """Performs actions before app is closed."""
        # prompt user to save changes (if any)
        if not self._layer_editor.save_old_file():
            return event.ignore()
        super(MainWindow, self).closeEvent(event)

    def undo(self):
        temp = undo.stack()
        self._layer_editor.le_model.gui_curr_block.selection.deselect_all()
        # Deselect because selected region can change and that could create wrong behaviour #
        self.curr_scene.hide_aux_point_and_seg()
        undo.stack().undo()
        self.update_all()

    def redo(self):
        temp = undo.stack()
        self._layer_editor.le_model.gui_curr_block.selection.deselect_all()
        # the same reason as in undo
        self.curr_scene.hide_aux_point_and_seg()
        undo.stack().redo()
        self.update_all()

    def update_all(self):
        self.curr_scene.update_scene()
        self.wg_regions_panel.update_tabs()
        self.layers.update_layers_panel()

    def change_curr_block(self, old_block_id):
        self.diagram_view.setScene(self.diagram_view.scenes[self._layer_editor.le_model.gui_curr_block.id])
        old_block = self._layer_editor.le_model.blocks_model.blocks.get(old_block_id)
        old_block.selection.selection_changed.disconnect(self.wg_regions_panel.selection_changed)
        curr_block = self._layer_editor.le_model.gui_curr_block
        curr_block.selection.selection_changed.connect(self.wg_regions_panel.selection_changed)
        self.wg_regions_panel.update_tabs()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Z and\
                event.modifiers() & QtCore.Qt.ControlModifier and\
                not event.modifiers() & QtCore.Qt.ShiftModifier:
            self.undo()
        elif event.key() == QtCore.Qt.Key_Z and\
                event.modifiers() & QtCore.Qt.ControlModifier and\
                event.modifiers() & QtCore.Qt.ShiftModifier:
            self.redo()

    def show_status_message(self, message, duration=5000):
        """Show a message in status bar for the given duration (in ms)."""
        self._status.showMessage(message, duration)

