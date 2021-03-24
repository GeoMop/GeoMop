"""Main Qt window.
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.layers_panel.layers_panel import LayerPanel
from LayerEditor.ui.menus.mesh import MeshMenu
from LayerEditor.ui.menus.edit import EditMenu
from LayerEditor.ui.panels.shapes_panel import ShapesPanel
from LayerEditor.ui.panels.surfaces import Surfaces
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
        self._layer_editor.le_model.gui_block_selector.value_changed.connect(self.change_curr_block)

        self._hsplitter.addWidget(self.diagram_view)

        self._hsplitter.setSizes([300, 760])

        # right pannels
        self._vsplitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self._vsplitter2.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.scroll_area2 = QtWidgets.QScrollArea()
        self.scroll_area2.setWidgetResizable(True)
        self.wg_surface_panel = Surfaces(self._layer_editor.le_model, self._layer_editor.save_file, parent=self.scroll_area2)
        self._show_grid(self._layer_editor.le_model.gui_block_selector.value is not None)
        self.scroll_area2.setWidget(self.wg_surface_panel)
        self._vsplitter2.addWidget(self.scroll_area2)

        self.shp_panel = ShapesPanel(self._layer_editor.le_model.shapes_model, self._vsplitter2)
        self._vsplitter2.addWidget(self.shp_panel)
        if self._layer_editor.le_model.shapes_model.is_empty():
            self.shp_panel.hide()

        if not self._layer_editor.le_model.shapes_model.is_empty():
            self.refresh_diagram_shp()

        # Menu bar
        self._menu = self.menuBar()
        self._edit_menu = EditMenu(self)
        self._file_menu = MainFileMenu(self, self._layer_editor)
        # self._analysis_menu = AnalysisMenu(self, cfg.config)
        # self._settings_menu = MainSettingsMenu(self, self._layer_editor)
        self._mesh_menu = MeshMenu(self, self._layer_editor)
        self.update_recent_files(0)
        if first:
            self._menu.addMenu(self._file_menu)
            self._menu.addMenu(self._edit_menu)
            # self._menu.addMenu(self._analysis_menu)
            # self._menu.addMenu(self._settings_menu)
            self._menu.addMenu(self._mesh_menu)

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
        self.wg_surface_panel.first_surface_added.connect(self._first_surface_added)
        self.shp_panel.background_changed.connect(self.refresh_diagram_shp)
        self.shp_panel.item_removed.connect(self.del_background_item)

        self._layer_editor.le_model.invalidate_scene.connect(self.update_scene)
        self._layer_editor.le_model.layers_changed.connect(self.layers_changed)

        self.wg_surface_panel.show_grid.connect(self._show_grid)

    def _first_surface_added(self, rect):
        if self._layer_editor.le_model.le_model_empty():
            self.diagram_view.set_init_area(rect)

    def update_recent_files(self, from_row=1):
        """Update recently opened files."""
        self._file_menu.update_recent_files(from_row)

    def refresh_diagram_shp(self):
        """refresh diagrams shape files background layer"""
        rect = self.diagram_view.refresh_shp_backgrounds()
        if not self._layer_editor.le_model.shapes_model.is_empty():
            if not self.shp_panel.isVisible():
                self.shp_panel.show()
            self.shp_panel.reload()
        else:
            self.shp_panel.hide()

        if self._layer_editor.le_model.le_model_empty(ignore_shapes=True) and\
                len(self._layer_editor.le_model.shapes_model.shapes) == 1 and\
                self.wg_surface_panel.data.name == "":
            dw = rect.width()/8
            dh = rect.height()/8
            rect.adjust(-dw, -dh, dw, dh)
            self.diagram_view.set_init_area(rect)
            self.diagram_view.fitInView(rect, QtCore.Qt.KeepAspectRatio)
        else:
            view_rect = self.diagram_view.mapToScene(self.diagram_view.viewport().geometry()).boundingRect()
            if not rect.intersects(view_rect):
                self.diagram_view.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def del_background_item(self, idx_item):
        """Remove background item"""
        obj = self._layer_editor.le_model.shapes_model.shapes[idx_item].shpdata.object
        obj.release_background()
        self.diagram_view.scene().removeItem(obj)
        del self._layer_editor.le_model.shapes_model.shapes[idx_item]

    def _cursor_changed(self, x, y):
        """Editor node change signal"""
        self._column.setText("x: {:5f}  y: {:5f}".format(x, -y))

    def layers_changed(self):
        self.update_all()

    def update_scene(self):
        self.curr_scene.update_scene()

    def _show_grid(self, show_flag):
        """Show mash"""
        if show_flag:
            quad, u_knots, v_knots = self.wg_surface_panel.get_curr_quad()
            if quad is None:
                return
            rect = self.diagram_view.show_grid(quad, u_knots, v_knots)
            view_rect = self.diagram_view.sceneRect()
            if not view_rect.contains(rect):
                view_rect = view_rect.united(rect)
                self.diagram_view.set_init_area(view_rect)
            self.diagram_view.fitInView(view_rect, QtCore.Qt.KeepAspectRatio)
        else:
            self.diagram_view.hide_grid()

    def closeEvent(self, event):
        """Performs actions before app is closed."""
        # prompt user to save changes (if any)
        if not self._layer_editor.save_old_file():
            return event.ignore()
        super(MainWindow, self).closeEvent(event)

    def undo(self):
        self._layer_editor.le_model.gui_block_selector.value.selection.deselect_all()
        # Deselect because selected region can change and that could create wrong behaviour #
        self.curr_scene.hide_aux_point_and_seg()
        undo.stack().undo()
        self.update_all()

    def redo(self):
        self._layer_editor.le_model.gui_block_selector.value.selection.deselect_all()
        # the same reason as in undo
        self.curr_scene.hide_aux_point_and_seg()
        undo.stack().redo()
        self.update_all()

    def update_all(self):
        self._layer_editor.le_model.validate_selectors()
        self.diagram_view.update_view()
        self.curr_scene.update_scene()
        self.wg_regions_panel.update_tabs()
        self.layers.update_layers_panel()
        self.wg_surface_panel.update_forms()

    def change_curr_block(self, old_block_id):
        if old_block_id is not None:
            old_block = self._layer_editor.le_model.blocks_model.get_item(old_block_id)
            old_block.selection.selection_changed.disconnect(self.wg_regions_panel.selection_changed)

        curr_block = self._layer_editor.le_model.gui_block_selector.value
        curr_block.selection.selection_changed.connect(self.wg_regions_panel.selection_changed)

        self.diagram_view.setScene(DiagramScene(curr_block, self._layer_editor.le_model.init_area, self.diagram_view))
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

