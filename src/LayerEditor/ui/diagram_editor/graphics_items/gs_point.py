from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import numpy as np

from LayerEditor.ui.data.region import Region
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.tools.cursor import Cursor


class GsPoint(QtWidgets.QGraphicsEllipseItem):
    SIZE = 6
    STD_ZVALUE = 20
    SELECTED_ZVALUE = 21
    __pen_table = {}

    no_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    add_brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)
    dim = 0

    @classmethod
    def make_pen(cls, color):
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(color, 1.4, QtCore.Qt.SolidLine)
        return (brush, pen)

    @classmethod
    def pen_table(cls, color):
        brush_pen = cls.__pen_table.setdefault(color, cls.make_pen(QtGui.QColor(color)))
        return brush_pen

    def __init__(self, pt, block):
        """ Initialize graphics point from data in pt.
            Calls fnc_init_attr to initialize pt.attr."""
        self.pt = pt
        self.block = block
        self.init_regions()
        # pt.gpt = self
        super().__init__(-self.SIZE, -self.SIZE, 2 * self.SIZE, 2 * self.SIZE)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        # do not scale points whenzooming
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        # Keep point shape (used for mouse interaction) having same size as the point itself.
        # self.setFlag(QtWidgets.QGraphicsItem.ItemClipsToShape, True)
        # self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        # Caching: Points can move.
        # if enabled QGraphicsScene.update() don't repaint

        self.setCursor(Cursor.point)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.update()

    @property
    def shape_id(self):
        return self.pt.id

    def init_regions(self):
        for layer in self.block.layers:
            if self.pt.id in layer.shape_regions[self.dim]:
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

    def paint(self, painter, option, widget):
        # print("option: ", option.state)
        if self.scene().selection.is_selected(self):
            painter.setBrush(GsPoint.no_brush)
            painter.setPen(self.region_pen)
        else:
            painter.setBrush(self.region_brush)
            painter.setPen(GsPoint.no_pen)
        painter.drawEllipse(self.rect())

    def update(self):
        self.prepareGeometryChange()
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPos(self.pt.xy[0], -self.pt.xy[1])
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        color = self.block.gui_selected_layer.get_shape_region(self).color
        self.region_brush, self.region_pen = GsPoint.pen_table(color)

        self.setZValue(self.STD_ZVALUE)
        super().update()

    def move_to(self, x, y):
        # self.pt.set_xy(x, y)
        displacement = np.array([x - self.pt.xy[0], -y - self.pt.xy[1]])
        if self.scene().decomposition.check_displacment([self.pt], displacement):
            self.scene().decomposition.move_points([self.pt], displacement)

        # for gseg in self.pt.g_segments():
        #     gseg.update()
        if self.scene():
            self.scene().update_all_segments()
            self.scene().update_all_polygons()
        self.update()
        return True

    def itemChange(self, change, value):
        """
        The item enables itemChange() notifications for
        ItemPositionChange, ItemPositionHasChanged, ItemMatrixChange,
        ItemTransformChange, ItemTransformHasChanged, ItemRotationChange,
        ItemRotationHasChanged, ItemScaleChange, ItemScaleHasChanged,
        ItemTransformOriginPointChange, and ItemTransformOriginPointHasChanged.
        """
        # print("change: ", change, "val: ", value)
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            # self.pt.set_xy(value.x(), value.y())
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

    def update_color(self, layer_id: int, regions: RegionsModel):
        brush, pen = self.pen_table(regions.regions[self.pt.attr].color)
        self.setPen(pen)
        self.setBrush(brush)