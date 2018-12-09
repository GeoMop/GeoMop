#!/usr/bin/env python
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import mouse

"""
TODO:
- selecting by right button
- pan for right button
- creating points/lines for right button
"""


class Region:

    _cols = ["cyan", "magenta", "red", "darkRed", "darkCyan", "darkMagenta",
             "green", "darkGreen", "yellow","blue"]
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 0

    def __init__(self):
        self.id = Region.id_next
        Region.id_next += 1
        self.color = Region.colors[self.id%len(Region.colors)].name()


class Point:
    def __init__(self, region):
        self.xy = np.random.randn(2)*100
        self.region = region

    def set_xy(self, x, y):
        print("move")
        self.xy[0] = x
        self.xy[1] = y


class Segment:
    def __init__(self, pt_from, pt_to, region):
        self.points = [pt_from, pt_to]
        self.region = region



class GsPoint(QtWidgets.QGraphicsEllipseItem):
    SIZE = 6
    STD_ZVALUE = 1
    SELECTED_ZVALUE = 0
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
        super().__init__(-self.SIZE, -self.SIZE, 2*self.SIZE, 2*self.SIZE, )
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)

        self.update()

    def paint(self, painter, option, widget):
        #print("option: ", option.state)
        if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
            painter.setBrush(GsPoint.no_brush)
            painter.setPen(self.region_pen)
        else:
            painter.setBrush(self.region_brush)
            painter.setPen(GsPoint.no_pen)
        painter.drawEllipse(self.rect())

    def update(self):
        self.setPos(self.pt.xy[0], self.pt.xy[1])
        self.region_brush, self.region_pen = GsPoint.pen_table(self.pt.region.color)
        self.setZValue(self.STD_ZVALUE)
        super().update()




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
            self.pt.set_xy(value.x(), value.y())
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
    STD_ZVALUE = 11
    SELECTED_ZVALUE = 10
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    add_pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen), WIDTH)


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

        print("seg")
        super().__init__()
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor)))
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()
        pass

    def update(self):
        pt_from, pt_to = self.segment.points
        self.setLine(pt_from.xy[0], pt_from.xy[1], pt_to.xy[0], pt_to.xy[1])
        self.region_pen, self.region_selected_pen  = GsSegment.pen_table(self.segment.region.color)
        super().update()

    def paint(self, painter, option, widget):
        if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
            painter.setPen(self.region_selected_pen)
        else:
            painter.setPen(self.region_pen)
        painter.drawLine(self.line())

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



class MainWindow(QtWidgets.QGraphicsView):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.points = []
        self.regions = []
        self.segments = []
        self.tmp_point = None
        self.tmp_segment = None

        self._zoom = 0
        self._empty = True
        self._scene = self.make_scene()
        #self._photo = QtWidgets.QGraphicsPixmapItem()
        #self._scene.addItem(self._photo)


        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        #self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


    def make_scene(self):
        # random data
        for r in range(5):
            self.regions.append(Region())

        for i in range(20):
            r_id = np.random.randint(0, len(self.regions), 1)[0]
            pt = Point(self.regions[r_id])
            self.points.append(pt)

        for i in range(20):
            r_id = np.random.randint(0, len(self.regions), 1)[0]
            p1, p2  = np.random.randint(0, len(self.points), 2)
            seg = Segment(self.points[p1], self.points[p2], self.regions[r_id])
            self.segments.append(seg)

        # make scene
        scene = QtWidgets.QGraphicsScene(self)
        for pt in self.points:
            scene.addItem(GsPoint(pt))
        for seg in self.segments:
            scene.addItem(GsSegment(seg))

        return scene

    def mouseDoubleClickEvent(self, QMouseEvent):
        pass

    def mousePressEvent(self, event):
        state = event.button() | event.modifiers()
        if event.button() == mouse.event.Left:
            below_item = self.items(event.scenePos())[0]
            self.new_point(event.scenePos(), below_item)

        elif event.button() == mouse.event.Right:
            # use panning/zooming functionality provided ofr the Left Button
            new_button = (event.button() ^ mouse.event.Right) | mouse.event.Left
            new_event = mouse.change_event(event, button = new_button)
            return super().mousePressEvent(new_event)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, QMouseEvent):
        pass

    #def mouseMoveEvent(self, QMouseEvent):

    def close_tmp_point(self):
        if self.tmp_point is None:
            return None
        self.points.append(self.tmp_point)
        self.tmp_point = None

    def close_tmp_segment(self):
        if self.tmp_segment is None:
            return None
        self.segments.append(self.tmp_segment)
        self.tmp_segment = None

    def make_point(self, pos, gitem):
        if type(gitem) == GsPoint:
            return gitem.pt
        elif type(gitem) == GsSegment:
            return gitem.split_segment(pos)
        else:
            return Point(pos, none_region)

    def extend_point(self, pos, gitem, close = False)

        last_pt = self.close_tmp_point()
        self.close_tmp_segment()
        self.tmp_point = self.make_point(pos, gitem)
        if last_pt:
            self.tmp_segment = Segment(last_pt, self.tmp_point, none_region)
        if close:
            self.close_tmp_point()
            self.close_tmp_line()


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
    mainWindow = MainWindow()
    mainWindow.setGeometry(500, 300, 800, 600)
    mainWindow.show()
    sys.exit(app.exec_())
