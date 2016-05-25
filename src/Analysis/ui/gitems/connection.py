import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class Connection(QtWidgets.QGraphicsPathItem):
    """ 
        Represents a join of nodes in the diagram
    """
    def __init__(self, connection, parent=None):
        super(Connection, self).__init__(parent)
        self._conn = connection
        self.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        #self.setFlags(self.ItemIsSelectable)
        self.setZValue(10)        
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.set_path()
        
    def set_path(self):
        """Set path as bezzier curve"""
        path = QtGui.QPainterPath()
        
        p1 = self._conn.get_in_pos()
        p2 = self._conn.get_out_pos()
        c1 = QtCore.QPointF(p1.x(), (p2.y()+p1.y())/2)
        c2 = QtCore.QPointF(p2.x(), (p2.y()+p1.y())/2)
        path.moveTo(p1)
        path.cubicTo(c1, c2, p2)
        self.setPath(path);      
      
    def need_repaint(self):
        """return if need repaint and nullify flag"""
        if self._conn.repaint:
            self._conn.repaint = False
            return True
        return False

#    def contextMenuEvent(self, event):
#        menu = QMenu()
#        menu.addAction('Delete')
#        pa = menu.addAction('Parameters')
#        pa.triggered.connect(self.editParameters)
#        menu.exec_(event.screenPos())
#
