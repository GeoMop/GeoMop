from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsRectItem

from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.data.tools.selector import Selector
from LayerEditor.ui.diagram_editor.graphics_items.diagramitem import DiagramItem
from LayerEditor.ui.tools.cursor import Cursor

from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment


class DiagramScene(QtWidgets.QGraphicsScene):
    regionsUpdateRequired = QtCore.pyqtSignal()

    def __init__(self, block, bounding_rect, parent):
        super().__init__(bounding_rect, parent)
        block.selection.set_diagram(self)
        self.selection = block.selection
        self.block = block

        self._diagrams = []     # do not modify directly! use appropriate methods
        self.add_diagram(DiagramItem(block))
        self.active_diagram = Selector(self._diagrams[0])

        self.last_point = None
        self.aux_pt, self.aux_seg = self.create_aux_segment()
        self.hide_aux_line()

        self._press_screen_pos = QtCore.QPoint()

        self.gs_surf_grid = None
        # holds graphics object for surface grid so it can be deleted when not needed

        self.update_scene()
        self.pixmap_item = None

        self.init_area = QGraphicsRectItem(self.sceneRect())
        self.init_area.setBrush(QBrush(Qt.NoBrush))
        pen = self.init_area.pen()
        pen.setCosmetic(True)
        self.init_area.setPen(pen)
        self.addItem(self.init_area)
        self.addItem(parent.root_shp_item)
        self.init_area.setVisible(parent._show_init_area)
        self.init_area.setZValue(-1000)

    def add_diagram(self, diagram):
        self._diagrams.append(diagram)
        self.addItem(diagram)

    def get_shape_color(self, shape_key):
        if self.block.gui_layer_selector.value is None:
            return "black"
        dim, shape_id = shape_key
        region = self.block.gui_layer_selector.value.shape_regions[dim][shape_id]

        if region is None:
            region = RegionItem.none
        return region.color

    def create_aux_segment(self):
        pt_size = GsPoint.SIZE
        no_pen = QtGui.QPen(QtCore.Qt.NoPen)
        add_brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)
        pt = self.addEllipse(-pt_size, -pt_size, 2*pt_size, 2*pt_size, no_pen, add_brush)
        pt.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        pt.setCursor(Cursor.draw)
        pt.setZValue(100)
        add_pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen), GsSegment.WIDTH)
        add_pen.setCosmetic(True)
        line = self.addLine(0,0,0,0, add_pen)
        line.setZValue(100)
        return pt, line


    def user_items_rect(self):
        """ Returns bounding rect of all items added by user.
            Those exclude any frames and other possible cosmetic items."""
        rect = QRectF()
        for point in self.points.values():
            rect = rect.united(point.mapToScene(point.boundingRect()).boundingRect())

        if self.parent().root_shp_item.childItems():
            root = self.parent().root_shp_item
            rect = rect.united(root.mapToScene(root.boundingRect()).boundingRect())

        if self.gs_surf_grid is not None:
            rect = rect.united(self.gs_surf_grid.mapToScene(self.gs_surf_grid.boundingRect()).boundingRect())

        return rect

    def move_aux_segment(self, tip, origin=None):
        """
        Update tip point and show aux segment and point.
        :param tip: Tip point (QPointF)
        :param origin: Origin point (QPointF)
        """
        self.aux_pt.show()
        self.aux_seg.show()
        self.aux_pt.setPos(tip)
        if origin is None:
            origin = self.aux_seg.line().p1()
        self.aux_seg.setLine(QtCore.QLineF(origin, tip))
        if origin.x() == tip.x() and origin.y() == tip.y():
            self.aux_seg.hide()

    def hide_aux_line(self):
        self.aux_pt.hide()
        self.aux_seg.hide()

    def new_point(self, pos, close=False):
        new_g_point = self.active_diagram.value.add_point(pos, self.last_point)

        if not close:
            self.last_point = new_g_point
            pt = new_g_point.pos()
            self.move_aux_segment(pt, origin=pt)
        else:
            self.last_point = None
            self.hide_aux_line()

        self.update_scene()

    def mouse_create_event(self, event):
        close = event.modifiers() & Qt.ControlModifier
        event.accept()
        self.selection._selected.clear()
        self.new_point(event.scenePos(), close)

    def below_item(self, scene_pos):
        below_item = None
        for item in self.items(scene_pos, deviceTransform=self.parent().transform()):
            if (item is self.aux_pt) or (item is self.aux_seg):
                continue
            below_item = item
            break
        return below_item

    def update_zoom(self, value):
        for diagram in self._diagrams:
            diagram.update_zoom(value)

    def mousePressEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        if event.button() == Qt.RightButton and self.last_point is None:
            self.parent().setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            for item in self.items():
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            self.selection.deselect_all()
        self._press_screen_pos = event.screenPos()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        below_item = self.below_item(event.scenePos())
        screen_pos_not_changed = (event.screenPos() - self._press_screen_pos).manhattanLength() < 5

        if event.button() == Qt.LeftButton and screen_pos_not_changed:
            self.mouse_create_event(event)

        if event.button() == Qt.RightButton and screen_pos_not_changed:
                self.selection_start_point = event.pos()
                item = None
                if below_item is not None:
                    if type(below_item) is GsPoint:
                        item = below_item
                    elif type(below_item) is GsSegment:
                        item = below_item
                    elif type(below_item) is GsPolygon:
                        item = below_item

                if event.modifiers() & Qt.ShiftModifier:
                    if item is not None:
                        self.selection.select_toggle_item(item)
                else:
                    if item is not None:
                        self.selection.select_item(item)
                    else:
                        self.selection.deselect_all()

        super().mouseReleaseEvent(event)
        if event.button() == Qt.RightButton:
            self.parent().setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            for item in self.items():
                item.block_select_change = True
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
                item.block_select_change = False

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super(DiagramScene, self).focusOutEvent(event)
        self.parent().setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mouseMoveEvent(self, event):
        # if event.buttons() & Qt.RightButton:
        #     rect_path = QPainterPath()
        #     rect_path.addRect(QRectF(self.selection_start_point, event.pos()))
        #     self.setSelectionArea(rect_path, self.parent().transform())
        #     for item in self.selectedItems():
        #         self.selection.add_selected_item(item)

        if self.last_point is not None:
            self.move_aux_segment(event.scenePos())
        super().mouseMoveEvent(event)

    def hide_aux_point_and_seg(self):
        self.last_point = None
        self.hide_aux_line()

    def keyPressEvent(self, event):
        """Standart key press event"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide_aux_point_and_seg()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.delete_selected()
        elif event.key() == QtCore.Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            self.selection.select_all()
        else:
            super(DiagramScene, self).keyPressEvent(event)

    def update_scene(self):
        # Show grid in this scene defined by parent view
        parent_surf_grid = self.parent().gs_surf_grid
        if parent_surf_grid is not self.gs_surf_grid:
            self.removeItem(self.gs_surf_grid)
            if parent_surf_grid is not None:
                self.addItem(parent_surf_grid)
            self.gs_surf_grid = parent_surf_grid

        for diagram in self._diagrams:
            diagram.update_item()

        self.update()

    def setSceneRect(self, rect: QtCore.QRectF) -> None:
        super(DiagramScene, self).setSceneRect(rect)
        self.init_area.setRect(rect)

    def delete_selected(self):
        self.decomposition.delete_items(self.selection.get_selected_shape_dim_id())
        self.update_scene()
        self.selection.deselect_all()
