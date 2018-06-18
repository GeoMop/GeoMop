import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .items_action import RequiredAction
from LayerEditor import definitions

class Connection(QtWidgets.QGraphicsPathItem):
    """ 
        Represents a join of nodes in the diagram
    """
    def __init__(self, connection, parent=None):
        super(Connection, self).__init__(parent)
        self._conn = connection
        self.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        self.setZValue(definitions.ZVALUE_CONNECTION)
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
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.items_action.item = self
        event.items_action.action = RequiredAction.conn_delete
        super(Connection, self). mousePressEvent(event)
        if event.items_action.item==self and event.button()==QtCore.Qt.RightButton:
            event.items_action.action = RequiredAction.conn_delete
            
    def get_point_desc(self, i):
        """return node description in set end (0 is output)"""
        if i==0:
            return self._conn.input.unique_name
        return self._conn.output.unique_name
        
