"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from LayerEditor.data import cfg
from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.panels.regions_panel import RegionsPanel
from LayerEditor.ui.tools.cursor import Cursor
from LayerEditor.ui.diagram_editor.diagram_view import DiagramView
# from .menus.edit import EditMenu
# from .menus.file import MainFileMenu
# from .menus.analysis import AnalysisMenu
# from .menus.settings import MainSettingsMenu
# from .menus.mesh import MeshMenu
import gm_base.icon as icon
# from .panels.new_diagram.diagram_view import DiagramView
# from .panels.new_diagram.tools import Cursor
from LayerEditor.ui.menus.file import MainFileMenu


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, layer_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()
        self._layer_editor = layer_editor
        self.make_widgets(True)

    @property
    def curr_scene(self):
        return self.diagramView.scene()

    @property
    def diagramView(self):
        return self._layer_editor.le_data.diagram_view

    def make_widgets(self, first=False):
        self.wg_regions_panel = RegionsPanel(self._layer_editor.le_data, self)

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
        #self.layers = panels.Layers(self.scroll_area1)
        #self.scroll_area1.setWidget(self.layers)
        self._vsplitter1.addWidget(self.scroll_area1)

        self._vsplitter1.addWidget(self.wg_regions_panel)

        # scene

        scene = self.diagramView.scenes[0]
        self.diagramView.setScene(scene)
        """scene is set here only temporarily until there will be more scenes  """
        self._hsplitter.addWidget(self.diagramView)

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

        self._status = self.statusBar()
        self._status.addPermanentWidget(self._reload_icon)
        self._status.addPermanentWidget(self._analysis_label)
        self._status.addPermanentWidget(self._column)
        self.setStatusBar(self._status)
        self._status.showMessage("Ready", 5000)

        # signals
        # self.shp.background_changed.connect(self.background_changed)
        # self.shp.item_removed.connect(self.del_background_item)
        # self.layers.viewInterfacesChanged.connect(self.refresh_view_data)
        # self.layers.editInterfaceChanged.connect(self.refresh_curr_data)
        # self.layers.topologyChanged.connect(self.set_topology)
        # self.layers.refreshArea.connect(self._refresh_area)
        # self.layers.clearDiagramSelection.connect(self.clear_diagram_selection)

        # cfg.layer_heads.region_changed.connect(self._region_changed)
        # cfg.layer_heads.selected_layer_changed.connect(self._region_changed)
        # TODO: This should be wrong, but seems to be same as in the master branch.
        self.wg_regions_panel.regions_changed.connect(self.curr_scene.update_scene)

        # self.wg_surface_panel.show_grid.connect(self._show_grid)

        # initialize components
        #self.config_changed()

    # def release_data(self, diagram):
    #     """Release all diagram graphic object"""
    #     self.diagramScene.release_data(diagram)
    #
    # def refresh_all(self):
    #     """For new data"""
    #     self.set_topology()
    #     if not cfg.diagram.shp.is_empty():
    #         # refresh deserialized shapefile
    #         cfg.diagram.recount_canvas()
    #         self.refresh_diagram_shp()
    #     self.diagramScene.set_data()
    #     self.layers.reload_layers(cfg)
    #     cfg.diagram.regions.reload_regions(cfg)
    #     self.refresh_view_data(0)
    #     self.update_layers_panel()
    #     self._refresh_area()
    #     if not cfg.diagram.position_set():
    #         self.display_area()
    #
    # def paint_new_data(self):
    #     """Propagate new diagram scene to canvas"""
    #     self.layers.change_size()
    #     #self.diagramScene.show_init_area(True)
    #     #if not cfg.config.show_init_area:
    #         #self.diagramScene.show_init_area(False)
    #     self.display_area()
    #
    # def refresh_curr_data(self, old_i, new_i):
    #     """Propagate new diagram scene to canvas"""
    #     if old_i == new_i:
    #         return
    #     self.refresh_view_data(old_i)
    #     self.refresh_view_data(new_i)
    #     self.diagramScene.release_data(old_i)
    #     self.diagramScene.set_data()
    #
    #     self._refresh_area()
    #
    #     view_rect = self.diagramView.rect()
    #     rect = QtCore.QRectF(cfg.diagram.x-100,
    #         cfg.diagram.y-100,
    #         view_rect.width()/cfg.diagram.zoom+200,
    #         view_rect.height()/cfg.diagram.zoom+200)
    #
    #     self.diagramScene.blink_start(rect)
    #
    def update_recent_files(self, from_row=1):
        """Update recently opened files."""
        self._file_menu.update_recent_files(from_row)
    #
    # def refresh_view_data(self, i):
    #     """Propagate new views (static, not edited diagrams)
    #     scene to canvas. i is changed view."""
    #     #self.diagramScene.update_views()
    #     self._move()
    #
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
    # def _cursor_changed(self, x, y):
    #     """Editor node change signal"""
    #     self._column.setText("x: {:5f}  y: {:5f}".format(x, -y))
    #
    # def _move(self):
    #     """zooming and moving"""
    #     view_rect = self.diagramView.rect()
    #     self._display(view_rect)
    #
    # def display_all(self):
    #     """Display all diagram"""
    #     #rect = cfg.diagram.rect
    #     #rect = cfg.diagram.get_diagram_all_rect(rect, cfg.layers, cfg.diagram_id())
    #     rect = self.diagramScene.itemsBoundingRect()
    #     self.display_rect(rect)
    #
    # def display_area(self):
    #     """Display area"""
    #     rect = cfg.diagram.get_area_rect(cfg.layers, cfg.diagram_id())
    #     self.display_rect(rect)
    #
    # def display_rect(self, rect):
    #     """Display set rect"""
    #     view_rect = self.diagramView.rect()
    #     if (view_rect.width()/rect.width())>(view_rect.height()/rect.height()):
    #         # resize acoording height
    #         cfg.diagram.zoom = view_rect.height()/rect.height()
    #         cfg.diagram.y = rect.top()
    #         cfg.diagram.x = rect.left()-(view_rect.width()/cfg.diagram.zoom-rect.width())/2
    #     else:
    #         cfg.diagram.zoom = view_rect.width()/rect.width()
    #         cfg.diagram.x = rect.left()
    #         cfg.diagram.y = rect.top()-(view_rect.height()/cfg.diagram.zoom-rect.height())/2
    #     if cfg.diagram.pen_changed:
    #         self.diagramScene.update_scene()
    #     self._display(view_rect)
    #
    # def get_display_rect(self):
    #     """Return display rect"""
    #     rect = self.diagramView.sceneRect()
    #     return rect
    #
    # def _display(self, view_rect):
    #     """moving"""
    #     self.diagramView.setSceneRect(
    #         cfg.diagram.x,
    #         cfg.diagram.y,
    #         view_rect.width()/cfg.diagram.zoom,
    #         view_rect.height()/cfg.diagram.zoom)
    #     transform = QtGui.QTransform(cfg.diagram.zoom, 0, 0,cfg.diagram.zoom, 0, 0)
    #     self.diagramView.setTransform(transform)
    #
    # def background_changed(self):
    #     """Background display shapefile paramaters was changed and
    #     shp items should be repainted"""
    #     self.diagramScene.refresh_shp_backgrounds()
    #
    # def del_background_item(self,  idx_item):
    #     """Remove backgroun item"""
    #     obj = cfg.diagram.shp.datas[idx_item].shpdata.object
    #     obj.release_background()
    #     self.diagramScene.removeItem(obj)
    #     del cfg.diagram.shp.datas[idx_item]
    #
    # def update_layers_panel(self):
    #     """Update layers panel"""
    #     self.layers.change_size()
    #
    # def set_topology(self):
    #     """Current topology or its structure is changed"""
    #     self.wg_regions.update_tabs()
    #
    # def clear_diagram_selection(self):
    #     """Selection has to be emptied"""
    #     self.diagramScene.selection.deselect_selected()
    #
    # def _update_regions(self):
    #     """Update region panel, eventually set tab according to the selection in diagram"""
    #     regions_of_layers = self.diagramScene.selection.get_selected_regions(cfg.diagram)
    #     if regions_of_layers:
    #         cfg.layer_heads.select_regions(dict(regions_of_layers))
    #
    #
    # def config_changed(self):
    #     """Handle changes of config."""
    #     analysis = cfg.analysis or '(No Analysis)'
    #     self._analysis_label.setText(analysis)

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
    #
    # def _refresh_area(self):
    #     """Refresh init area"""
    #     #if self.diagramScene.init_area is not None:
    #     #   self.diagramScene.init_area.reload()
    #     pass
    #
    # def closeEvent(self, event):
    #     """Performs actions before app is closed."""
    #     # prompt user to save changes (if any)
    #     if not self._layer_editor.save_old_file():
    #         return event.ignore()
    #     super(MainWindow, self).closeEvent(event)

    def show_status_message(self, message, duration=5000):
        """Show a message in status bar for the given duration (in ms)."""
        self._status.showMessage(message, duration)

