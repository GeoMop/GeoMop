import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Polygon(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = -11
    
    def __init__(self, polygon, parent=None):
        super(Polygon, self).__init__(polygon.spolygon.gtpolygon)
        self.polygon = polygon 
        polygon.object = self
        """polygon data object"""
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 232))
        self.setBrush(brush)
        self.setZValue(self.STANDART_ZVALUE) 
        
    def release_polygon(self):
        self.polygon.object = None
