import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem, QWidget

from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.diagram_editor.graphics_items.abstract_graphics_item import AbstractGraphicsItem
from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment


class DiagramItem(AbstractGraphicsItem):
    TOLERANCE = 5

    def __init__(self, layer: LayerItem, zoom):
        super(DiagramItem, self).__init__()
        self.shapes = [{}, {}, {}]  # [points, segments, polygons]
        self.points = {}
        self.segments = {}
        self.polygons = {}
        """Maps to all graphical objects grouped by type {id:QGraphicsItem}"""

        self.layer = layer

        # polygons
        self.decomposition = layer.block.decomposition
        self.decomposition.poly_decomp.set_tolerance(self.TOLERANCE)

        self.update_item(zoom)
        self.setZValue(1)

    @property
    def data_item(self):
        return self.layer

    @property
    def id(self):
        """Temporary way to identify diagram. Will be changed when view panel exists"""
        return self.layer.block.id

    def enable_editing(self):
        self.enable_interactions(True)
        self.scene().selection = self.layer.block.selection

    def disable_editing(self):
        self.enable_interactions(False)
        if self.scene() is not None:
            self.scene().selection = None

    def enable_interactions(self, enable=True):
        if enable:
            self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        else:
            self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

    def update_item(self, zoom=None):
        # points
        to_remove = []
        de_points = self.decomposition.points
        for point_id in self.points:
            if point_id not in de_points:
                to_remove.append(point_id)
        for point_id in to_remove:
            self.remove_child_item(self.points[point_id])
            del self.points[point_id]
        for point_id, point in de_points.items():
            if point_id in self.points:
                self.points[point_id].update()
            else:
                gpt = GsPoint(point, self.layer)
                self.points[point_id] = gpt
                gpt.setParentItem(self)

        # segments
        to_remove = []
        de_segments = self.decomposition.segments
        for segment_id in self.segments:
            if segment_id not in de_segments:
                to_remove.append(segment_id)
        for segment_id in to_remove:
            self.remove_child_item(self.segments[segment_id])
            del self.segments[segment_id]
        for segment_id, segment in de_segments.items():
            if segment_id in self.segments:
                self.segments[segment_id].update()
            else:
                gseg = GsSegment(segment, self.layer)
                gseg.update_zoom(zoom if zoom is not None else self.scene().parent().zoom)
                self.segments[segment_id] = gseg
                gseg.setParentItem(self)

        # polygons
        to_remove = []
        de_polygons = self.decomposition.polygons
        for polygon_id in self.polygons:
            if polygon_id not in de_polygons:
                to_remove.append(polygon_id)
        for polygon_id in to_remove:
            self.remove_child_item(self.polygons[polygon_id])
            del self.polygons[polygon_id]
        for polygon_id, polygon in de_polygons.items():
            if polygon.outer_wire.is_root():
                continue
            if polygon_id in self.polygons:
                self.polygons[polygon_id].update()
            else:
                gpol = GsPolygon(polygon, self.layer)
                self.polygons[polygon_id] = gpol
                gpol.setParentItem(self)

    def update_zoom(self, value):
        self.decomposition.poly_decomp.set_tolerance(self.TOLERANCE/value)
        for g_seg in self.segments.values():
            g_seg.update_zoom(value)

    def add_point(self, pos, last_point=None):
        """Add continuous line and point, from self.last_point"""
        new_point = self.decomposition.new_point(pos, last_point)
        if new_point.id in self.points:
            return self.points[new_point.id]
        else:
            new_g_point = GsPoint(new_point, self.layer)
            self.points[new_point.id] = new_g_point
            new_g_point.setParentItem(self)
            return new_g_point

    def update_all_points(self):
        for g_point in self.points.values():
            g_point.update()

    def update_all_segments(self):
        for g_seg in self.segments.values():
            g_seg.update()

    def update_all_polygons(self):
        for g_pol in self.polygons.values():
            g_pol.update()

    def boundingRect(self) -> QtCore.QRectF:
        return self.childrenBoundingRect()

    def paint(self, painter: QtGui.QPainter,
              option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        pass

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(DiagramItem, self).mousePressEvent(event)

    def remove_child_item(self, item):
        item.setParentItem(None)
        self.scene().removeItem(item)