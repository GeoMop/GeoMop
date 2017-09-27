import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class InitArea(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = -1000
    
    def __init__(self, area, parent=None):
        super(InitArea, self).__init__(area.gtpolygon)
        self.area = area 
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        brush = QtGui.QBrush(QtGui.QColor(246, 246, 246))
        self.setBrush(brush)
        self.setZValue(self.STANDART_ZVALUE) 
 
    
