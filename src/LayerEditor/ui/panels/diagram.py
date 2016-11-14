"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
from ui.gitems import Line, Point

class Diagram(QtWidgets.QGraphicsScene):
    """GeoMop design area"""

    def __init__(self, data, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        self._data = data
        """Diagram data"""
        self._conn = []
        """List of connections"""
        self.selected_node = None
        """selected node"""
        self.repairing_connection = None
        """
        If connection is about changes, is in this variable 
        
        """
        super(Diagram, self).__init__(parent)        
        self.set_data(data)        
        
    def set_data(self, data):
        self._data = data
        self.clear()
        for line in data.lines:
            l = Line(line)
            self.addItem(l) 
        for point in data.points:
            p = Point(point)
            self.addItem(p)

    def mouseMoveEvent(self, event):
        """Standart mouse event"""
        super(Diagram, self).mouseMoveEvent(event)
        pass
            
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self). mousePressEvent(event)
