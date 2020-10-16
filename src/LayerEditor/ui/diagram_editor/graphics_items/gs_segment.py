from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import numpy as np

from LayerEditor.ui.data.region import Region
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.tools.cursor import Cursor


class GsSegment(QtWidgets.QGraphicsLineItem):
    __pen_table={}

    WIDTH = 3.0
    STD_ZVALUE = 10
    SELECTED_ZVALUE = 11
    no_pen = QtGui.QPen(QtCore.Qt.NoPen)
    dim = 1


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

    def __init__(self, segment, block):
        """ Initialize graphics segment from data in segment.
            Calls fnc_init_attr to initialize segment.attr """
        self.segment = segment
        self.init_regions(block)
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

    def init_regions(self, block):
        for layer in block.layers:
            if self.segment.id in layer.shape_regions[self.dim]:
                return
            else:
                region = layer.gui_selected_region
                dim = self.dim
                if not layer.is_fracture:
                    dim += 1
                if region.dim == dim:
                    layer.shape_regions[self.dim][self.segment.id] = layer.gui_selected_region
                else:
                    layer.shape_regions[self.dim][self.segment.id] = Region.none

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
            key = (1, self.segment.id)
            color = self.scene().get_shape_color(key)
        self.region_pen, self.region_selected_pen  = GsSegment.pen_table(color)

        super().update()

    def paint(self, painter, option, widget):
        #if option.state & (QtWidgets.QStyle.State_Sunken | QtWidgets.QStyle.State_Selected):
        if self.scene().selection.is_selected(self):
            painter.setPen(self.region_selected_pen)
        else:
            painter.setPen(self.region_pen)
        painter.drawLine(self.line())

    def move_to(self, x, y):
        #self.pt.set_xy(x, y)
        displacement = np.array([x - self.pos().x(), -y + self.pos().y()])
        if self.scene().decomposition.check_displacment([self.segment.vtxs[0], self.segment.vtxs[1]], displacement):
            self.scene().decomposition.move_points([self.segment.vtxs[0], self.segment.vtxs[1]], displacement)

        # for gseg in self.pt.g_segments():
        #     gseg.update()
        if self.scene():
            self.scene().update_all_points()
            self.scene().update_all_segments()
            self.scene().update_all_polygons()
        self.update()

    def itemChange(self, change, value):
        #print("change: ", change, "val: ", value)
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            self.move_to(value.x(), value.y())
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if self.isSelected():
                self.setZValue(self.SELECTED_ZVALUE)
            else:
                self.setZValue(self.STD_ZVALUE)
        return super().itemChange(change, value)

    def update_zoom(self, value):
        pen = QtGui.QPen()
        pen.setWidthF(self.WIDTH / value)
        self.setPen(pen)


    def update_color(self, layer_id: int, regions: RegionsModel):
        pen, selected_pen = self.pen_table(regions.regions[self.segment.attr].color)
        self.setPen(pen)
