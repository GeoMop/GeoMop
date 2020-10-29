from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import numpy as np

from LayerEditor.ui.data.region import Region
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.tools.cursor import Cursor

class GsPolygon(QtWidgets.QGraphicsPolygonItem):
    __brush_table={}

    SQUARE_SIZE = 20
    STD_ZVALUE = 0
    SELECTED_ZVALUE = 1
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    dim = 2


    @classmethod
    def make_brush(cls, color):
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        return brush

    @classmethod
    def brush_table(cls, color):
        brush = cls.__brush_table.setdefault(color, cls.make_brush(QtGui.QColor(color)))
        return brush

    def __init__(self, polygon, block):
        """ Initialize graphics polygon from data in polygon.
            Calls fnc_init_attr to initialize polygon.attr """
        self.polygon_data = polygon
        self.block = block
        self.init_regions()
        #polygon.g_polygon = self
        self.painter_path = None
        self.depth = 0
        super().__init__()
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        #self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        # if enabled QGraphicsScene.update() don't repaint
        self.setPen(self.no_pen)
        self.setCursor(Cursor.polygon)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()

    @property
    def shape_id(self):
        return self.polygon_data.id

    def init_regions(self):
        for layer in self.block.layers:
            if self.polygon_data.id in layer.shape_regions[self.dim]:
                return
            else:
                region = layer.gui_selected_region
                dim = self.dim
                if not layer.is_fracture:
                    dim += 1
                if region.dim == dim:
                    layer.set_region_to_shape(self, layer.gui_selected_region)
                else:
                    layer.set_region_to_shape(self, Region.none)

    def update(self):
        self.prepareGeometryChange()
        points = self.polygon_data.vertices()
        qtpolygon = QtGui.QPolygonF()
        for i in range(len(points)):
            qtpolygon.append(QtCore.QPointF(points[i].xy[0], -points[i].xy[1]))
        qtpolygon.append(QtCore.QPointF(points[0].xy[0], -points[0].xy[1]))

        self.setPolygon(qtpolygon)

        self.painter_path = self._get_polygon_draw_path(self.polygon_data)

        color = self.block.gui_selected_layer.get_shape_region(self).color
        self.region_brush = GsPolygon.brush_table(color)

        self.depth = self.polygon_data.depth()
        self.setZValue(self.STD_ZVALUE + self.depth)

        super().update()

    def paint(self, painter, option, widget):
        painter.setPen(self.no_pen)
        #if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
        if self.scene().selection.is_selected(self):
            brush = QtGui.QBrush(self.region_brush)
            brush.setStyle(QtCore.Qt.Dense4Pattern)
            tr = painter.worldTransform()
            brush.setTransform(QtGui.QTransform.fromScale(self.SQUARE_SIZE / tr.m11(), self.SQUARE_SIZE / tr.m22()))
            painter.setBrush(brush)
        else:
            painter.setBrush(self.region_brush)
        painter.drawPath(self.painter_path)

    def itemChange(self, change, value):
        #print("change: ", change, "val: ", value)
        #if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
        #    self.pt.set_xy(value.x(), value.y())
        # if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
        #     if self.isSelected():
        #         self.setZValue(self.SELECTED_ZVALUE)
        #     else:
        #         self.setZValue(self.STD_ZVALUE)
        return super().itemChange(change, value)

    @staticmethod
    def _get_wire_oriented_vertices(wire):
        """
        Follow the wire segments and get the list of its vertices duplicating the first/last point.
        return: array, shape: n_vtx, 2
        """
        seggen = wire.segments()
        vtxs = []
        for seg, side in seggen:
            # Side corresponds to the end point of the segment. (Indicating also on which side thenwire lies.)
            if not vtxs:
                # first segment - add both vertices, so the loop is closed at the end.
                other_side = not side
                vtxs.append(seg.vtxs[other_side].xy)
            vtxs.append(seg.vtxs[side].xy)
        return np.array(vtxs)

    @classmethod
    def _add_to_painter_path(cls, path, wire):
        vtxs = cls._get_wire_oriented_vertices(wire)
        point_list = [QtCore.QPointF(vtxx, -vtxy) for vtxx, vtxy in vtxs]
        sub_poly = QtGui.QPolygonF(point_list)
        path.addPolygon(sub_poly)

    def _get_polygon_draw_path(self, polygon):
        """Get the path to draw the polygon in, i.e. the outer boundary and inner boundaries.
        The path approach allows holes in polygons and therefore flat depth for polygons (Odd-even paint rule)"""
        complex_path = QtGui.QPainterPath()
        self._add_to_painter_path(complex_path, polygon.outer_wire)
        # Subtract all inner parts
        for inner_wire in polygon.outer_wire.childs:
            self._add_to_painter_path(complex_path, inner_wire)
        return complex_path

