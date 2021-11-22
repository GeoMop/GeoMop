from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QPolygonF, QPen
from PyQt5.QtWidgets import QGraphicsItemGroup

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.diagram_editor.graphics_items.grid import Grid
from LayerEditor.ui.diagram_editor.graphics_items.shp_background import ShpBackground


class DiagramView(QtWidgets.QGraphicsView):
    cursorChanged = pyqtSignal(float, float)

    def __init__(self, le_model):
        super(DiagramView, self).__init__()
        self.le_model = le_model
        self.gs_surf_grid = None
        self._empty = True
        self.root_shp_item = QGraphicsItemGroup()
        self._show_init_area = True

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        self.el_map = {}

        scale = le_model.init_zoom_pos_data["zoom"]
        self.scale(scale, scale)
        self.centerOn(QPointF(le_model.init_zoom_pos_data["x"],
                              -le_model.init_zoom_pos_data["y"]))

        self.setScene(DiagramScene(le_model.gui_block_selector.value, self.le_model.init_area, self))

    def show_grid(self, quad, u_knots, v_knots):
        """ Create grid of currently selected surface from surface panel.
            This object is shown in update of a scene."""
        if quad is None:
            return
        self.gs_surf_grid = Grid(quad, u_knots, v_knots)
        self.scene().update_scene()
        return self.gs_surf_grid.boundingRect()

    def hide_grid(self):
        self.gs_surf_grid = None
        self.scene().update_scene()

    def set_show_init_area(self, state):
        self._show_init_area = state
        self.scene().init_area.setVisible(state)

    def display_all(self):
        rect = self.scene().user_items_rect()

        if not self.scene().sceneRect().contains(rect):
            # if there is stuff outside scene rect `fitInView()` doesn't work properly
            # solution project items rect through center and find bounding rect with projected rect included
            center = self.scene().sceneRect().center()
            new_rect = QRectF(rect)
            new_rect.moveCenter(-(new_rect.center() - center))
            rect = rect.united(new_rect)

        self.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def display_area(self):
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            scale = 1.25
        else:
            scale = 0.8
        self.scale(scale, scale)
        self.scene().update_zoom(self.zoom)

    @property
    def zoom(self):
        return self.transform().m11()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super(DiagramView, self).mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.cursorChanged.emit(pos.x(), pos.y())

    def setScene(self, scene: DiagramScene) -> None:
        super(DiagramView, self).setScene(scene)
        self.scene().update_zoom(self.zoom)
        scene.update_scene()

    def save(self):
        center = self.mapToScene(self.viewport().rect().center())

        return {"init_area": [(point.x(), -point.y()) for point in QPolygonF(self.sceneRect())][:-1],
                "zoom": {"zoom": self.zoom,
                         "x": center.x(),
                         "y": -center.y(),
                         'position_set': False}}

    def update_view(self):
        if self.scene().block is not self.le_model.gui_block_selector.value:
            self.setScene(DiagramScene(self.le_model.gui_block_selector.value,
                                       self.le_model.init_area,
                                       self))

    def set_init_area(self, rect: QRectF):
        self.le_model.init_area = rect
        self.scene().setSceneRect(rect)

    def refresh_shp_backgrounds(self):
        """refresh updated shape files on background and return rect of affected shapes"""
        rect = QRectF()
        for shp in self.le_model.shapes_model.shapes:
            if shp.shpdata.object is None:
                s = ShpBackground(shp.shpdata, shp.color)
                self.root_shp_item.addToGroup(s)
                shp.refreshed = True
                rect = rect.united(s.boundingRect())
            elif not shp.refreshed:
                shp.shpdata.object.color = shp.color
                shp.shpdata.object.update()
                shp.refreshed = True
                rect = rect.united(shp.shpdata.object.boundingRect())
        return rect





