import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from leconfig import cfg

class ShpBackground(QtWidgets.QGraphicsItem):
    """ 
        Represents a join of nodes in the diagram
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
        if cfg.diagram.pen.widthF() != painter.pen().widthF():
            pen = QtGui.QPen(cfg.diagram.pen)
            painter.setPen(pen)
            bpen = QtGui.QPen(cfg.diagram.bpen)
        if painter.pen().color()!= self.color:
            pen = QtGui.QPen(cfg.diagram.pen)
            pen.setColor( self.color)
            painter.setPen(pen)
            bpen = QtGui.QPen(cfg.diagram.bpen)
            bpen.setColor( self.color)
            
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        highlighted = False
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
