import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Point(QtWidgets.QGraphicsEllipseItem):
    """ 
    Represents a block in the diagram 
    """
   
    def __init__(self, point,data, parent=None):
        """if item is selected"""
        self._point = point
        self.data = data
        super(Point, self).__init__(self._point.x-2*data.zoom, 
            self._point.y-2*data.zoom, 4*data.zoom, 4*data.zoom, parent)   
        self.setPen(self.data.pen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))     
        
    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that change line with accoding zoom"""
        if self.data.pen.widthF() != self.pen().widthF():
            self.prepareGeometryChange()
            self.setRect(self._point.x-2/self.data.zoom, 
                self._point.y-2/self.data.zoom, 4/self.data.zoom, 4/self.data.zoom)
            self.setPen(self.data.pen)
        super(Point, self).paint(painter, option, widget)

 
    def mousePressEvent(self,event):
        """Standart mouse event"""        
        event.gobject = self
        
