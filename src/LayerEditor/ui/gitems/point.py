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
        point.object = self
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
        
    def move_point(self, pos):
        """Move point to new pos and move all affected lines"""
        self._point.x = pos.x()
        self._point.y = pos.y()
        self.setRect(self._point.x-2*self.data.zoom, 
            self._point.y-2*self.data.zoom, 4*self.data.zoom, 4*self.data.zoom) 
        for line in self._point.lines:
            line.object.move_line()
            
    def shift_point(self, shift):
        """Move point to new pos and move all affected lines"""
        pos = QtCore.QPointF(self._point.x, self._point.y) + shift
        self.move_point(pos)
        
    def mousePressEvent(self,event):
        """Standart mouse event"""        
        event.gobject = self

        
