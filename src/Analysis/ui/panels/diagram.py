"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
from ui.gitems import Node, Connection

class Diagram(QtWidgets.QGraphicsScene):
    """GeoMop design area"""

    def __init__(self, data, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        self._data = data
        self._conn = []
        """List of connections"""
        super(Diagram, self).__init__(parent)        
        self.set_data(data)        
        
    def set_data(self, data):
        self._data = data
        self.clear()
        self._conn = []
        for node in data.nodes:
            n = Node(node)
            self.addItem(n) 
        for conn in data.connections:
            c = Connection(conn)
            self.addItem(c)  
            self._conn.append(c)            
    
    def dragMoveEvent(self, event):
        """Qt standart event"""
        self._data.mark_invalid_connections()
        for conn in self._conn:
            if conn.need_repaint():
                conn.update()        

    def mouseMoveEvent(self, mouseEvent):
        # editor.sceneMouseMoveEvent(mouseEvent)
        super(Diagram, self).mouseMoveEvent(mouseEvent)
        item = self.mouseGrabberItem() 
        if item is not None:
            item.mark_invalid()
            self._data.mark_invalid_connections()
            for conn in self._conn:
                if conn.need_repaint():
                    conn.set_path()
                    #conn.update()      
        
    def mouseReleaseEvent(self, mouseEvent):
        # editor.sceneMouseReleaseEvent(mouseEvent)
        super(Diagram
        , self).mouseReleaseEvent(mouseEvent)
