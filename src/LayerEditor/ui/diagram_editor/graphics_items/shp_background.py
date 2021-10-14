import time

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from LayerEditor.ui.diagram_editor.graphics_items.abstract_graphics_item import AbstractGraphicsItem


class ShpBackground(AbstractGraphicsItem):
    """ 
        Represents a shp file diagram background
    """
    
    ZVALUE = -10
    PEN_WIDTH = 1.4
    BPEN_WIDTH = 3.5
    
    def __init__(self, shp_item, parent=None):
        super(ShpBackground, self).__init__(parent)
        self._shp_item = shp_item
        self.shp = shp_item.shpdata
        """shape file objects data"""
        self.color = shp_item.color
        """shape file objects data color"""
        self.shp.object = self
        self.setZValue(self.ZVALUE)
        self.pen = QtGui.QPen(self.color)
        self.pen.setWidthF(self.PEN_WIDTH)
        self.pen.setCosmetic(True)
        self.bpen = QtGui.QPen(self.color)
        self.bpen.setWidthF(self.BPEN_WIDTH)
        self.bpen.setCosmetic(True)

    def update_item(self):
        pass

    @property
    def data_item(self):
        return self._shp_item

    def boundingRect(self):
        """Redefination of standart boundingRect function, that return bound rect"""
        r = self.BPEN_WIDTH
        rect = QtCore.QRectF(self.shp.min, self.shp.max)
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget):
        self.pen.setColor(self.color)
        r = self.PEN_WIDTH
        painter.setPen(self.pen)
        self.bpen.setColor(self.color)

        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        highlighted = False
        for line in self.shp.lines:
            if line.highlighted != highlighted:
                highlighted = line.highlighted
                if highlighted:
                    painter.setPen(self.bpen)
                else:
                    painter.setPen(self.pen)
            painter.drawLine(line.p1, line.p2)
        for point in self.shp.points:
            if point.highlighted != highlighted:
                highlighted = point.highlighted
                if highlighted:
                    painter.setPen(self.bpen)
                else:
                    painter.setPen(self.pen)
            painter.drawEllipse(point.p, r, r)
        painter.setPen(self.pen)
         
    def release_background(self):
        self.shp.object.setParentItem(None)
        self.shp.object = None        
