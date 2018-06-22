import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from LayerEditor.leconfig import cfg


class ShpBackground(QtWidgets.QGraphicsItem):
    """ 
        Represents a shp file diagram background
    """
    
    ZVALUE = -10
    
    def __init__(self, shp, color, parent=None):
        super(ShpBackground, self).__init__(parent)
        self.shp = shp
        """shape file objects data"""
        self.color = color
        """shape file objects data color"""
        shp.object = self        
        self.setZValue(self.ZVALUE) 
        
    def boundingRect(self):
        """Redefination of standart boundingRect function, that return boun rect"""
        r = cfg.diagram.pen.widthF()
        rect = QtCore.QRectF(self.shp.min, self.shp.max)
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that paint object from shape file"""
        r = cfg.diagram.pen.widthF()
        
        pen = QtGui.QPen(cfg.diagram.pen)
        pen.setColor(self.color)
        painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(self.color.red(),self.color.green(),self.color.blue(),10))
        painter.setBrush(brush)
        bpen = QtGui.QPen(cfg.diagram.bpen)
        bpen.setColor( self.color)
        bbrush = QtGui.QBrush(QtGui.QColor(self.color.red(),self.color.green(),self.color.blue(),50))
            
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        highlighted = False
        for polygon in self.shp.polygons:
            if polygon.highlighted != highlighted:
                highlighted = polygon.highlighted
                if highlighted:
                    painter.setPen(bpen)
                    painter.setBrush(bbrush)
                else:
                    painter.setPen(pen)
                    painter.setBrush(brush)
            painter.drawPolygon(polygon.polygon_points)
        for line in self.shp.lines:
            if line.highlighted != highlighted:
                highlighted = line.highlighted
                if highlighted:
                    painter.setPen(bpen)
                else:
                    painter.setPen(pen)
            painter.drawLine(line.p1, line.p2)
        for point in self.shp.points:
            if point.highlighted != highlighted:
                highlighted = point.highlighted
                if highlighted:
                    painter.setPen(bpen)
                else:
                    painter.setPen(pen)
            painter.drawEllipse(point.p, r, r)
        painter.setPen(pen)
         
    def release_background(self):
        self.shp.object = None        
