import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Line(QtWidgets.QGraphicsLineItem):
    """ 
        Represents a join of nodes in the diagram
    """
    def __init__(self, line, data, parent=None):
        super(Line, self).__init__(line.p1.x, line.p1.y, line.p2.x, line.p2.y, parent)
        self._line = line
        line.object = self
        """Line data object"""
        self.data = data        
        self.setPen(self.data.pen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that change line with accoding zoom"""
        if self.data.pen.widthF() != self.pen().widthF():
            self.setPen(self.data.pen)
        super(Line, self).paint(painter, option, widget)
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
        
    def move_line(self):
        """Move line"""
        self.setLine(self._line.p1.x, self._line.p1.y, self._line.p2.x, self._line.p2.y)
        
    def shift_line(self, shift):
        """shift line"""
        self._line.p1.object.shift_point(shift)
        self._line.p2.object.shift_point(shift)
