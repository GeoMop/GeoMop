#!/usr/bin/env python
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import mouse


"""
TODO:

- switch buttons
- decomposition:
  wrapper classes: Point, Segment, Polygon (merge with GsPoint etc. add additional info)
  keep both diretion relation to GsPoint, are organized 
  into a dict using same decomp IDs, keep back reference to decomp objects.
   
- move lines with points
- decomposition two modes - with and without intersection tracking, with and without polygons
- add decomposition
"""

class Cursor:
    @classmethod
    def setup_cursors(cls):
        cls.point =  QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        cls.segment = QtGui.QCursor(QtCore.Qt.UpArrowCursor)
        cls.polygon = QtGui.QCursor(QtCore.Qt.CrossCursor)
        cls.draw = QtGui.QCursor(QtCore.Qt.ArrowCursor)

class Region:
    _cols = ["cyan", "magenta", "red", "darkRed", "darkCyan", "darkMagenta",
             "green", "darkBlue", "yellow","blue"]
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 0



    def __init__(self, id = None, color = None ):
        if id is None:
            id = Region.id_next
            Region.id_next += 1
        self.id = id

        if color is None:
            color = Region.colors[self.id%len(Region.colors)].name()
        self.color = color

# Special instances
Region.none =  Region(0, "grey")




class Point:
    def __init__(self, x, y, region):
        self.gpt = None
        self.xy = np.array([x, y])
        self.region = region

    def set_xy(self, x, y):
        print("point move")
        self.xy[0] = x
        self.xy[1] = y

        # testing boundary
        if x < 200:
            self.xy[0] = 200

    def segments(self):
        """
        Generator of connected segments.
        :return:
        """

    def g_segments(self):
        """
        Generator of graphical segments.
        :return:
        """
        for seg in self.segments():
            yield seg.g_segment


class Segment:
    def __init__(self, pt_from, pt_to, region):
        self.g_segment = None
        self.points = [pt_from, pt_to]
        self.region = region


class Polygon:
    def __init__(self, segments, region):
        self.g_polygon = None
        self.segments = list(segments)
        self.region = region



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
        pt.gpt = self
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
        print("option: ", option.state)
        #if option.state & QtWidgets.QStyle.State_Selected:
        if self.scene().selection.is_selected(self.pt):
            painter.setBrush(GsPoint.no_brush)
            painter.setPen(self.region_pen)
        else:
            painter.setBrush(self.region_brush)
            painter.setPen(GsPoint.no_pen)
        painter.drawEllipse(self.rect())

    def update(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(self.pt.xy[0], self.pt.xy[1])
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.region_brush, self.region_pen = GsPoint.pen_table(self.pt.region.color)
        self.setZValue(self.STD_ZVALUE)
        super().update()


    def move_to(self, x, y):
        self.pt.set_xy(x, y)
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
        segment.g_segment = self
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
        pt_from, pt_to = self.segment.points
        #self.setLine(pt_from.xy[0], pt_from.xy[1], pt_to.xy[0], pt_to.xy[1])
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(QtCore.QPointF(pt_from.xy[0], pt_from.xy[1]))
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setLine(0, 0, pt_to.xy[0] - pt_from.xy[0], pt_to.xy[1] - pt_from.xy[1])
        self.region_pen, self.region_selected_pen  = GsSegment.pen_table(self.segment.region.color)
        super().update()

    def paint(self, painter, option, widget):
        #if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
        if self.scene().selection.is_selected(self.segment):
            painter.setPen(self.region_selected_pen)
        else:
            painter.setPen(self.region_pen)
        painter.drawLine(self.line())

    def itemChange(self, change, value):
        #print("change: ", change, "val: ", value)
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # set new values to data layer
            p0 = self.segment.points[0]
            p1 = self.segment.points[1]
            p0.set_xy(p0.xy[0] + value.x() - self.pos().x(), p0.xy[1] + value.y() - self.pos().y())
            p1.set_xy(p1.xy[0] + value.x() - self.pos().x(), p1.xy[1] + value.y() - self.pos().y())

            # update graphic layer
            p0.gpt.update()
            p1.gpt.update()
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
        polygon.g_polygon = self
        super().__init__()
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        #self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        # if enabled QGraphicsScene.update() don't repaint

        self.setCursor(Cursor.polygon)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.setZValue(self.STD_ZVALUE)
        self.update()

    def update(self):
        def com_point(seg1, seg2):
            p0 = seg1.points[0]
            if (p0 is seg2.points[0]) or (p0 is seg2.points[1]):
                return p0
            p1 = seg1.points[1]
            if (p1 is seg2.points[0]) or (p1 is seg2.points[1]):
                return p1
            return None

        def pol_append(pol, seg1, seg2):
            p = com_point(seg1, seg2)
            pol.append(QtCore.QPointF(p.xy[0], p.xy[1]))

        pol = QtGui.QPolygonF()
        segs = self.polygon_data.segments
        pol_append(pol, segs[-1], segs[0])
        for i in range(len(self.polygon_data.segments) - 1):
            pol_append(pol, segs[i], segs[i+1])

        self.setPolygon(pol)
        self.region_brush = GsPolygon.brush_table(self.polygon_data.region.color)
        super().update()

    def paint(self, painter, option, widget):
        painter.setPen(self.no_pen)
        #if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
        if self.scene().selection.is_selected(self.polygon_data):
            brush = QtGui.QBrush(self.region_brush)
            brush.setStyle(QtCore.Qt.Dense4Pattern)
            tr = painter.worldTransform()
            brush.setTransform(QtGui.QTransform.fromScale(self.SQUARE_SIZE / tr.m11(), self.SQUARE_SIZE / tr.m22()))
            painter.setBrush(brush)
        else:
            painter.setBrush(self.region_brush)
        painter.drawPolygon(self.polygon())

    def itemChange(self, change, value):
        #print("change: ", change, "val: ", value)
        #if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
        #    self.pt.set_xy(value.x(), value.y())
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if self.isSelected():
                self.setZValue(self.SELECTED_ZVALUE)
            else:
                self.setZValue(self.STD_ZVALUE)
        return super().itemChange(change, value)


class TmpPoint(Point):
    def __init__(self):
        super().__init__(0, 0, Region.adding)

class TmpSegment(Segment):
    def __init__(self):
        super().__init__(0, 0, Region.adding)


class Selection():
    def __init__(self, diagram):
        self._diagram = diagram
        self._selected = []

    def select_item(self, item):
        self.deselect_all()
        self.select_add_item(item)
        self._diagram.update()

    def select_add_item(self, item):
        if item in self._selected:
            self._selected.remove(item)
        else:
            self._selected.append(item)
        self._diagram.update()

    def select_all(self):
        self._selected.clear()
        self._selected.extend(self._diagram.points)
        self._selected.extend(self._diagram.segments)
        self._selected.extend(self._diagram.polygons)
        self._diagram.update()

    def deselect_all(self):
        self._selected.clear()
        self._diagram.update()

    def is_selected(self, item):
        return item in self._selected


class Diagram(QtWidgets.QGraphicsScene):

    def __init__(self, parent):
        rect = QtCore.QRectF(0,0,1000,1000)
        super().__init__(rect, parent)
        self.points = []
        self.regions = []
        self.segments = []
        self.polygons = []

        self.last_point = None
        self.aux_pt, self.aux_seg = self.create_aux_segment()
        self.hide_aux_line()

        self._zoom_value = 1.0
        self.selection = Selection(self)
        self._press_screen_pos = QtCore.QPoint()

        # testing boundary
        pen = QtGui.QPen()
        pen.setWidthF(0)
        self.addLine(200, 0, 200, 1000, pen)

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

    def hide_aux_line(self):
        self.aux_pt.hide()
        self.aux_seg.hide()



    def add_point(self, pos, gitem):
        if type(gitem) == GsPoint:
            return gitem
        else:
            #if type(gitem) == GsSegment:
            pt = Point(pos.x(), pos.y(), Region.none)
            gpt = GsPoint(pt)
            self.points.append(pt)
            self.addItem(gpt)
            return gpt

    def add_segment(self, gpt1, gpt2):
        seg = Segment(gpt1.pt, gpt2.pt, Region.none)
        gseg = GsSegment(seg)
        gseg.update_zoom(self._zoom_value)
        self.segments.append(seg)
        self.addItem(gseg)

        # add polygon, try only one possible path
        def get_next_seg_point(s_last, p_last):
            p_last_segs = []
            for s in self.segments:
                if p_last in s.points:
                    p_last_segs.append(s)
            for s in p_last_segs:
                if s is not s_last:
                    if s.points[0] == p_last:
                        return s, s.points[1]
                    else:
                        return s, s.points[0]
            return None, None

        seg_list = [seg]
        s_last = seg
        p_last = gpt2.pt
        while True:
            s_next, p_next = get_next_seg_point(s_last, p_last)
            if s_next is None:
                break
            if s_next in seg_list:
                self.add_polygon(seg_list)
                break
            else:
                seg_list.append(s_next)
                s_last = s_next
                p_last = p_next

    def add_polygon(self, segments):
        pol = Polygon(segments, Region.none)
        gpol = GsPolygon(pol)
        self.polygons.append(pol)
        self.addItem(gpol)

    def new_point(self, pos, gitem, close = False):
        #print("below: ", gitem)
        new_g_point = self.add_point(pos, gitem)
        if self.last_point is not None:
            self.add_segment(self.last_point, new_g_point)
        if not close:
            self.last_point = new_g_point
            pt = new_g_point.pos()
            self.move_aux_segment(pt, origin=pt)
        else:
            self.last_point = None
            self.hide_aux_line()

    def mouse_create_event(self, event):
        #transform = self.parent().transform()
        #below_item = self.itemAt(event.scenePos(), transform)
        below_item = self.below_item(event.scenePos())
        close = event.modifiers() & mouse.Event.Ctrl
        self.new_point(event.scenePos(), below_item, close)
        event.accept()

    def below_item(self, scene_pos):
        below_item = None
        for item in self.items(scene_pos, deviceTransform=self.parent().transform()):
            if (item is self.aux_pt) or (item is self.aux_seg):
                continue
            below_item = item
            break
        return below_item

    def update_zoom(self, value):
        self._zoom_value = value

        for seg in self.segments:
            seg.g_segment.update_zoom(value)

    def update_all_segments(self):
        for seg in self.segments:
            seg.g_segment.update()

    def update_all_polygons(self):
        for pol in self.polygons:
            pol.g_polygon.update()

    def mousePressEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        #print("P last: ", event.lastScenePos())
        # if event.button() == mouse.Event.Right and self.last_point is None:
        #     self.mouse_create_event(event)

        self._press_screen_pos = event.screenPos()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        #print("R last: ", event.lastScenePos())
        below_item = self.below_item(event.scenePos())
        screen_pos_not_changed = event.screenPos() == self._press_screen_pos

        if event.button() == mouse.Event.Left and screen_pos_not_changed:
            self.mouse_create_event(event)

        if event.button() == mouse.Event.Right and screen_pos_not_changed:
            data_item = None
            if below_item is not None:
                if type(below_item) is GsPoint:
                    data_item = below_item.pt
                elif type(below_item) is GsSegment:
                    data_item = below_item.segment
                elif type(below_item) is GsPolygon:
                    data_item = below_item.polygon_data

            if event.modifiers() & mouse.Event.Shift:
                if data_item is not None:
                    self.selection.select_add_item(data_item)
            else:
                if data_item is not None:
                    self.selection.select_item(data_item)
                else:
                    self.selection.deselect_all()

        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if self.last_point is not None:
            self.move_aux_segment(event.scenePos())
        super().mouseMoveEvent(event)


class DiagramView(QtWidgets.QGraphicsView):
    def __init__(self):

        super(DiagramView, self).__init__()
        print(self)


        self._zoom = 0
        self._empty = True
        self._scene = Diagram(self)
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        #self.setFrameShape(QtWidgets.QFrame.Box)
        #self.ensureVisible(self._scene.sceneRect())
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)



    #def mouseDoubleClickEvent(self, QMouseEvent):
    #    pass


    # def mousePressEvent(self, event):
    #     return super().mousePressEvent(mouse.event_swap_buttons(event, QtCore.QEvent.MouseButtonPress))
    #
    # def mouseReleaseEvent(self, event):
    #     return super().mouseReleaseEvent(mouse.event_swap_buttons(event, QtCore.QEvent.MouseButtonRelease))
    #
    # def mouseMoveEvent(self, event):
    #     return super().mouseMoveEvent(mouse.event_swap_buttons(event, QtCore.QEvent.MouseMove))






    # def hasPhoto(self):
    #     return not self._empty
    #
    # def fitInView(self, scale=True):
    #     rect = QtCore.QRectF(self._photo.pixmap().rect())
    #     if not rect.isNull():
    #         self.setSceneRect(rect)
    #         if self.hasPhoto():
    #             unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
    #             self.scale(1 / unity.width(), 1 / unity.height())
    #             viewrect = self.viewport().rect()
    #             scenerect = self.transform().mapRect(rect)
    #             factor = min(viewrect.width() / scenerect.width(),
    #                          viewrect.height() / scenerect.height())
    #             self.scale(factor, factor)
    #         self._zoom = 0
    #
    # def setPhoto(self, pixmap=None):
    #     self._zoom = 0
    #     if pixmap and not pixmap.isNull():
    #         self._empty = False
    #         self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
    #         self._photo.setPixmap(pixmap)
    #     else:
    #         self._empty = True
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #         self._photo.setPixmap(QtGui.QPixmap())
    #     self.fitInView()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        self.scale(factor, factor)

        self._scene.update_zoom(self.transform().m11())

    # def toggleDragMode(self):
    #     if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
    #         self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
    #     elif not self._photo.pixmap().isNull():
    #         self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    # def mousePressEvent(self, event):
    #     if self._photo.isUnderMouse():
    #         self.photoClicked.emit(QtCore.QPoint(event.pos()))
    #     super(PhotoViewer, self).mousePressEvent(event)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Cursor.setup_cursors()
    mainWindow = DiagramView()
    mainWindow.setGeometry(500, 300, 800, 600)
    mainWindow.show()
    sys.exit(app.exec_())
