from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np

from LayerEditor.ui.panels.new_diagram.region import Region
from LayerEditor.ui.panels.new_diagram.tools import Cursor


class GsPoint(QtWidgets.QGraphicsEllipseItem):
    SIZE = 6
    STD_ZVALUE = 20
    SELECTED_ZVALUE = 21
    __pen_table={}

    no_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    add_brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)

    @classmethod
    def make_pen(cls, color):
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(color, 1.4, QtCore.Qt.SolidLine)
        return (brush, pen)

    @classmethod
    def pen_table(cls, color):
        brush_pen = cls.__pen_table.setdefault(color, cls.make_pen(QtGui.QColor(color)))
        return brush_pen

    def __init__(self, pt):
        self.pt = pt
        #pt.gpt = self
        super().__init__(-self.SIZE, -self.SIZE, 2*self.SIZE, 2*self.SIZE, )
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            # do not scale points whenzooming
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
            # Keep point shape (used for mouse interaction) having same size as the point itself.
        #self.setFlag(QtWidgets.QGraphicsItem.ItemClipsToShape, True)
        #self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
            # Caching: Points can move.
        # if enabled QGraphicsScene.update() don't repaint

        self.setCursor(Cursor.point)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()

    def paint(self, painter, option, widget):
        #print("option: ", option.state)
        #if option.state & QtWidgets.QStyle.State_Selected:
        if self.scene().selection.is_selected(self):
            painter.setBrush(GsPoint.no_brush)
            painter.setPen(self.region_pen)
        else:
            painter.setBrush(self.region_brush)
            painter.setPen(GsPoint.no_pen)
        painter.drawEllipse(self.rect())

    def update(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(self.pt.xy[0], -self.pt.xy[1])
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        color = Region.none.color
        if self.scene():
            regions = self.scene().regions
            key = (1, self.pt.id)
            reg_id = regions.get_shape_region(key)
            color = regions.regions[reg_id].color
        self.region_brush, self.region_pen = GsPoint.pen_table(color)

        self.setZValue(self.STD_ZVALUE)
        super().update()


    def move_to(self, x, y):
        #self.pt.set_xy(x, y)
        displacement = np.array([x - self.pt.xy[0], -y - self.pt.xy[1]])
        if self.scene().decomposition.check_displacment([self.pt], displacement):
            self.scene().decomposition.move_points([self.pt], displacement)

        # for gseg in self.pt.g_segments():
        #     gseg.update()
        if self.scene():
            self.scene().update_all_segments()
            self.scene().update_all_polygons()
        self.update()


    def itemChange(self, change, value):
        """
        The item enables itemChange() notifications for
        ItemPositionChange, ItemPositionHasChanged, ItemMatrixChange,
        ItemTransformChange, ItemTransformHasChanged, ItemRotationChange,
        ItemRotationHasChanged, ItemScaleChange, ItemScaleHasChanged,
        ItemTransformOriginPointChange, and ItemTransformOriginPointHasChanged.
        """
        #print("change: ", change, "val: ", value)
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            #self.pt.set_xy(value.x(), value.y())
            self.move_to(value.x(), value.y())
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if self.isSelected():
                self.setZValue(self.SELECTED_ZVALUE)
            else:
                self.setZValue(self.STD_ZVALUE)
        return super().itemChange(change, value)


    # def mousePressEvent(self, event):
    #     self.update()
    #     super().mousePressEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     self.update()
    #     super().mouseReleaseEvent(event)



class GsPoint2(QtWidgets.QGraphicsEllipseItem):
    SIZE = 6
    STD_ZVALUE = 20+7
    SELECTED_ZVALUE = 21+7
    __pen_table={}

    no_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    add_brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)

    @classmethod
    def make_pen(cls, color):
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(color, 1.4, QtCore.Qt.SolidLine)
        return (brush, pen)

    @classmethod
    def pen_table(cls, color):
        brush_pen = cls.__pen_table.setdefault(color, cls.make_pen(QtGui.QColor(color)))
        return brush_pen

    def __init__(self, x, y, color):
        self.my_x = x
        self.my_y = y
        self.color = color
        super().__init__(-self.SIZE, -self.SIZE, 2*self.SIZE, 2*self.SIZE, )
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        # do not scale points whenzooming
        #self.setCursor(Cursor.point)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()

    def paint(self, painter, option, widget):
        if self.scene().selection.is_selected(self):
            painter.setBrush(GsPoint.no_brush)
            painter.setPen(self.region_pen)
        else:
            painter.setBrush(self.region_brush)
            painter.setPen(GsPoint.no_pen)
        painter.drawEllipse(self.rect())

    def update(self):
        self.setPos(self.my_x, self.my_y)

        self.region_brush, self.region_pen = GsPoint.pen_table(self.color)

        self.setZValue(self.STD_ZVALUE)
        super().update()


class GsSegment(QtWidgets.QGraphicsLineItem):
    __pen_table={}

    WIDTH = 3.0
    STD_ZVALUE = 10
    SELECTED_ZVALUE = 11
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)


    @classmethod
    def make_pen(cls, color):
        pen = QtGui.QPen(color, cls.WIDTH, QtCore.Qt.SolidLine)
        pen.setCosmetic(True)
        selected_pen = QtGui.QPen(color, cls.WIDTH, QtCore.Qt.DashLine)
        selected_pen.setCosmetic(True)
        return (pen, selected_pen)

    @classmethod
    def pen_table(cls, color):
        pens = cls.__pen_table.setdefault(color, cls.make_pen(QtGui.QColor(color)))
        return pens

    def __init__(self, segment):
        self.segment = segment
        #segment.g_segment = self
        super().__init__()
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        #self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        # if enabled QGraphicsScene.update() don't repaint

        self.setCursor(Cursor.segment)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.setZValue(self.STD_ZVALUE)
        self.update()

    def update(self):
        #pt_from, pt_to = self.segment.points
        pt_from, pt_to = self.segment.vtxs[0], self.segment.vtxs[1]
        #self.setLine(pt_from.xy[0], pt_from.xy[1], pt_to.xy[0], pt_to.xy[1])
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(QtCore.QPointF(pt_from.xy[0], -pt_from.xy[1]))
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setLine(0, 0, pt_to.xy[0] - pt_from.xy[0], -pt_to.xy[1] + pt_from.xy[1])

        color = Region.none.color
        if self.scene():
            regions = self.scene().regions
            key = (2, self.segment.id)
            reg_id = regions.get_shape_region(key)
            color = regions.regions[reg_id].color
        self.region_pen, self.region_selected_pen  = GsSegment.pen_table(color)

        super().update()

    def paint(self, painter, option, widget):
        #if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
        if self.scene().selection.is_selected(self):
            painter.setPen(self.region_selected_pen)
        else:
            painter.setPen(self.region_pen)
        painter.drawLine(self.line())

    def itemChange(self, change, value):
        #print("change: ", change, "val: ", value)
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # set new values to data layer
            p0 = self.segment.vtxs[0]
            p1 = self.segment.vtxs[1]
            diff = np.array([value.x() - self.pos().x(), value.y() - self.pos().y()])
            p0.move(diff)
            p1.move(diff)

            # update graphic layer
            #p0.gpt.update()
            #p1.gpt.update()
            self.scene().update_all_segments()
            self.scene().update_all_polygons()

            return self.pos()
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if self.isSelected():
                self.setZValue(self.SELECTED_ZVALUE)
            else:
                self.setZValue(self.STD_ZVALUE)
        return super().itemChange(change, value)

    def update_zoom(self, value):
        pen = QtGui.QPen()
        pen.setWidthF(self.WIDTH * 2 / value)
        self.setPen(pen)


class GsPolygon(QtWidgets.QGraphicsPolygonItem):
    __brush_table={}

    SQUARE_SIZE = 20
    STD_ZVALUE = 0
    SELECTED_ZVALUE = 1
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)


    @classmethod
    def make_brush(cls, color):
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        return brush

    @classmethod
    def brush_table(cls, color):
        brush = cls.__brush_table.setdefault(color, cls.make_brush(QtGui.QColor(color)))
        return brush

    def __init__(self, polygon):
        self.polygon_data = polygon
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

        self.setCursor(Cursor.polygon)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()

    def update(self):
        points = self.polygon_data.vertices()
        qtpolygon = QtGui.QPolygonF()
        for i in range(len(points)):
            qtpolygon.append(QtCore.QPointF(points[i].xy[0], -points[i].xy[1]))
        qtpolygon.append(QtCore.QPointF(points[0].xy[0], -points[0].xy[1]))

        self.setPolygon(qtpolygon)

        self.painter_path = self._get_polygon_draw_path(self.polygon_data)

        color = Region.none.color
        if self.scene():
            regions = self.scene().regions
            key = (3, self.polygon_data.id)
            reg_id = regions.get_shape_region(key)
            color = regions.regions[reg_id].color
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
