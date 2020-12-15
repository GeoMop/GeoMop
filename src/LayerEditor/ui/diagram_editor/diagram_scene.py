from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsRectItem

from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.tools.cursor import Cursor

from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment


class DiagramScene(QtWidgets.QGraphicsScene):
    regionsUpdateRequired = QtCore.pyqtSignal()
    TOLERANCE = 5

    def __init__(self, block, bounding_rect, parent):
        super().__init__(bounding_rect, parent)
        block.selection.set_diagram(self)
        self.selection = block.selection
        self.block = block
        self.shapes = [{}, {}, {}]  # [points, segments, polygons]
        self.points = {}
        self.segments = {}
        self.polygons = {}
        """Maps to all graphical objects grouped by type {id:QGraphicsItem}"""

        self.regions_model = block.regions_model

        self.last_point = None
        self.aux_pt, self.aux_seg = self.create_aux_segment()
        self.hide_aux_line()

        self._press_screen_pos = QtCore.QPoint()

        # polygons
        self.decomposition = block.decomposition
        self.decomposition.set_tolerance(self.TOLERANCE)

        self.gs_surf_grid = None
        # holds graphics object for surface grid so it can be deleted when not needed

        self.update_scene()
        self.pixmap_item = None
        self.b_box = QGraphicsRectItem(self.sceneRect())
        self.b_box.setBrush(QBrush(Qt.NoBrush))
        pen = self.b_box.pen()
        pen.setCosmetic(True)
        self.b_box.setPen(pen)
        self.addItem(self.b_box)

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

    def add_point(self, pos):
        """Add continuous line and point, from self.last_point"""
        new_point = self.decomposition.new_point(pos, self.last_point)
        if new_point.id in self.points:
            return self.points[new_point.id]
        else:
            new_g_point = GsPoint(new_point, self.block)
            self.points[new_point.id] = new_g_point
            self.addItem(new_g_point)
            return new_g_point

    def new_point(self, pos, close=False):
        new_g_point = self.add_point(pos)

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
        self.decomposition.set_tolerance(self.TOLERANCE/value)
        for g_seg in self.segments.values():
            g_seg.update_zoom(value)

    def update_all_points(self):
        for g_point in self.points.values():
            g_point.update()

    def update_all_segments(self):
        for g_seg in self.segments.values():
            g_seg.update()

    def update_all_polygons(self):
        for g_pol in self.polygons.values():
            g_pol.update()

    def mousePressEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """

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


    def mouseMoveEvent(self, event):
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
                self.removeItem(self.gs_surf_grid)
                self.addItem(parent_surf_grid)
                self.b_box.setRect(self.sceneRect())
            self.gs_surf_grid = parent_surf_grid

        # points
        to_remove = []
        de_points = self.decomposition.points
        for point_id in self.points:
            if point_id not in de_points:
                to_remove.append(point_id)
        for point_id in to_remove:
            self.removeItem(self.points[point_id])
            del self.points[point_id]
        for point_id, point in de_points.items():
            if point_id in self.points:
                self.points[point_id].update()
            else:
                gpt = GsPoint(point, self.block)
                self.points[point_id] = gpt
                self.addItem(gpt)

        # segments
        to_remove = []
        de_segments = self.decomposition.segments
        for segment_id in self.segments:
            if segment_id not in de_segments:
                to_remove.append(segment_id)
        for segment_id in to_remove:
            self.removeItem(self.segments[segment_id])
            del self.segments[segment_id]
        for segment_id, segment in de_segments.items():
            if segment_id in self.segments:
                self.segments[segment_id].update()
            else:
                gseg = GsSegment(segment, self.block)
                parent = self.parent()
                gseg.update_zoom(self.parent().zoom)
                self.segments[segment_id] = gseg
                self.addItem(gseg)

        # polygons
        to_remove = []
        de_polygons = self.decomposition.polygons
        for polygon_id in self.polygons:
            if polygon_id not in de_polygons:
                to_remove.append(polygon_id)
        for polygon_id in to_remove:
            self.removeItem(self.polygons[polygon_id])
            del self.polygons[polygon_id]
        for polygon_id, polygon in de_polygons.items():
            if polygon.outer_wire.is_root():
                continue
            if polygon_id in self.polygons:
                self.polygons[polygon_id].update()
            else:
                gpol = GsPolygon(polygon, self.block)
                self.polygons[polygon_id] = gpol
                self.addItem(gpol)

        self.update()

    def delete_selected(self):
        self.decomposition.delete_items(self.selection.get_selected_shape_dim_id())
        self.update_scene()