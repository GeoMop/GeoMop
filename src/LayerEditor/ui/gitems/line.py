import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates, get_state_color

class Line(QtWidgets.QGraphicsLineItem):
    """ 
        Represents a join of nodes in the diagram
    """
    def __init__(self, line, data, parent=None):
        super(Line, self).__init__(line.p1.x, line.p1.y, line.p2.x, line.p2.y, parent)
        self.line = line
        self._tmp = False
        line.object = self
        """Line data object"""
        self.state = ItemStates.standart
        """Item state"""
        self.data = data        
        self.setPen(self.data.pen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setZValue(10) 
        
    def set_tmp(self):
        """set style and z"""
        self._tmp = True
        self.state = ItemStates.added
        self.setZValue(0)        

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that change line with accoding zoom"""
        if self.data.pen.widthF() != self.pen().widthF():
            self.setPen(self.data.pen)
        if self.pen().color()!=get_state_color(self.state):
            pen = QtGui.QPen(self.data.pen)
            pen.setColor(get_state_color(self.state))
            self.setPen(pen)
        super(Line, self).paint(painter, option, widget)
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Line, self).mousePressEvent(event)
        else:
            event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Line, self).mouseReleaseEvent(event)
        else:
            event.gobject = self
        
    def move_line(self, new_state=None):
        """Move line"""
        if new_state is not None:
            self.state = new_state
        self.setLine(self.line.p1.x, self.line.p1.y, self.line.p2.x, self.line.p2.y)
        
    def shift_line(self, shift, new_state=None):
        """shift line"""
        self.line.p1.object.shift_point(shift, new_state)
        self.line.p2.object.shift_point(shift, new_state)
        
    def release_line(self):
        self.line.object = None
        self.data = None
