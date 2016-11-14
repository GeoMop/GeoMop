import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Point(QtWidgets.QGraphicsEllipseItem):
    """ 
    Represents a block in the diagram 
    """
   
    def __init__(self, point, parent=None):
        self.selected = False
        """if item is selected"""
        super(Point, self).__init__(point.x, point.y, 4, 2, parent)        
        self._point = point
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
 
    def mousePressEvent(self,event):
        """Standart mouse event"""        
        event.gobject = self
