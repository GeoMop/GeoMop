import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Line(QtWidgets.QGraphicsLineItem):
    """ 
        Represents a join of nodes in the diagram
    """
    def __init__(self, line, parent=None):
        super(Line, self).__init__(line.p1.x, line.p1.y, line.p2.x, line.p2.y, parent)
        self._line = line
        """Line data object"""
        self.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
