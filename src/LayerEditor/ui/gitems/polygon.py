import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Polygon(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    MIN_ZVALUE = -999
    DEFAUT_COLOR = "#f0f0e8"
    
    def __init__(self, polygon, parent=None):
        super(Polygon, self).__init__(polygon.qtpolygon)
        self.polygon = polygon 
        polygon.object = self
        """polygon data object"""
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.color = polygon.get_color()
        self.depth = polygon.depth
        if self.color=="##":
            brush = QtGui.QBrush(QtGui.QColor(self.DEFAUT_COLOR))
        else:
            brush = QtGui.QBrush(QtGui.QColor(self.color))
        self.setBrush(brush)
        self.setZValue(self.MIN_ZVALUE+self.depth) 
        
    def update_color(self):
        color = self.polygon.get_color()
        if self.color != color:
            self.color = color
            if color=="##":
                color = self.DEFAUT_COLOR
            brush = QtGui.QBrush(QtGui.QColor(color))
            self.setBrush(brush)
            self.update()
            
    def update_depth(self):
        """Check and set polygon depth"""
        if self.depth != self.polygon.depth:
            self.depth = self.polygon.depth
            self.setZValue(self.MIN_ZVALUE+self.depth)
        
    def release_polygon(self):
        self.polygon.object = None
        
    def refresh_polygon(self):
        """reload polygon.spolygon.gtpolygon"""
        self.setPolygon(self.polygon.qtpolygon)
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
