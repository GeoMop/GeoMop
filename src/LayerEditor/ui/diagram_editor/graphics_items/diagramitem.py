import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem, QWidget

from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment


class DiagramItem(QGraphicsItem):
    TOLERANCE = 5

    def __init__(self,  block):
        super(DiagramItem, self).__init__()
        self.shapes = [{}, {}, {}]  # [points, segments, polygons]
        self.points = {}
        self.segments = {}
        self.polygons = {}
        """Maps to all graphical objects grouped by type {id:QGraphicsItem}"""

        # polygons
        self.decomposition = block.decomposition
        self.decomposition.poly_decomp.set_tolerance(self.TOLERANCE)

        self.block = block
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)

    def update_item(self):
        # points
        to_remove = []
        de_points = self.decomposition.points
        for point_id in self.points:
            if point_id not in de_points:
                to_remove.append(point_id)
        for point_id in to_remove:
            #self.removeItem(self.points[point_id])
            del self.points[point_id]
        for point_id, point in de_points.items():
            if point_id in self.points:
                self.points[point_id].update()
            else:
                gpt = GsPoint(point, self.block)
                self.points[point_id] = gpt
                gpt.setParentItem(self)

        # segments
        to_remove = []
        de_segments = self.decomposition.segments
        for segment_id in self.segments:
            if segment_id not in de_segments:
                to_remove.append(segment_id)
        for segment_id in to_remove:
            #self.removeItem(self.segments[segment_id])
            del self.segments[segment_id]
        for segment_id, segment in de_segments.items():
            if segment_id in self.segments:
                self.segments[segment_id].update()
            else:
                gseg = GsSegment(segment, self.block)
                gseg.update_zoom(self.scene().parent().zoom)
                self.segments[segment_id] = gseg
                gseg.setParentItem(self)

        # polygons
        to_remove = []
        de_polygons = self.decomposition.polygons
        for polygon_id in self.polygons:
            if polygon_id not in de_polygons:
                to_remove.append(polygon_id)
        for polygon_id in to_remove:
            #self.removeItem(self.polygons[polygon_id])
            del self.polygons[polygon_id]
        for polygon_id, polygon in de_polygons.items():
            if polygon.outer_wire.is_root():
                continue
            if polygon_id in self.polygons:
                self.polygons[polygon_id].update()
            else:
                gpol = GsPolygon(polygon, self.block)
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
            new_g_point = GsPoint(new_point, self.block)
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

