import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class ShpBackground(QtWidgets.QGraphicsItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    ZVALUE = -10
    
    def __init__(self, shp, data, color, parent=None):
        super(ShpBackground, self).__init__(parent)
        self.shp = shp
        """shape file objects data"""
        self.color = color
        """shape file objects data color"""
        shp.object = self        
        self.data = data        
        self.setZValue(self.ZVALUE) 
        
    def boundingRect(self):
        """Redefination of standart boundingRect function, that return boun rect"""
        r = self.data.pen.widthF()
        rect = QtCore.QRectF(self.shp.min, self.shp.max)
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that paint object from shape file"""
        r = self.data.pen.widthF()
        if self.data.pen.widthF() != painter.pen().widthF():
            painter.setPen(self.data.pen)
        if painter.pen().color()!= self.color:
            pen = QtGui.QPen(self.data.pen)
            pen.setColor( self.color)
            painter.setPen(pen)
        highlighted = False
        painter.setOpacity(0.3)
        for line in self.shp.lines:
            if line.highlighted != highlighted:
                highlighted = line.highlighted
                if highlighted:
                    painter.setOpacity(0.6)
                else:
                    painter.setOpacity(0.3)
            painter.drawLine(line.p1, line.p2)
        for point in self.shp.points:
            if point.highlighted != highlighted:
                highlighted = point.highlighted
                if highlighted:
                    painter.setOpacity(0.6)
                else:
                    painter.setOpacity(0.3)
            painter.drawEllipse(point.p, r, r)
            
    def release_point(self):
        self.shp.object = None
        self.data = None
        
