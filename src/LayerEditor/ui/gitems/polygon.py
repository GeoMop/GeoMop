import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates
from LayerEditor.leconfig import cfg
from LayerEditor import definitions

class Polygon(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """

    DEFAUT_COLOR = "#f0f0e8"
    
    def __init__(self, polygon_data, parent=None):
        super().__init__(polygon_data.qtpolygon, parent)
        self.polygon_data = polygon_data
        polygon_data.object = self
        """polygon data object"""
        self.state = ItemStates.standart
        """Item state"""
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        #self.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor))
        self.setZValue(definitions.ZVALUE_POLYGON)
        self.update_brush()

    def update_geometry(self):
        """Update geometry according to actual zoom"""
        self.update_brush()

    def update_color(self):
        """Update color to actual color"""
        self.update_brush()

    def update_brush(self):
        if self.state == ItemStates.selected:
            brush = QtGui.QBrush(cfg.diagram.brush_selected)
        else:
            brush = QtGui.QBrush(cfg.diagram.brush)

        color = self.polygon_data.get_color()
        if color == "##":
            color = self.DEFAUT_COLOR
        brush.setColor(QtGui.QColor(color))

        self.setBrush(brush)

    def release_polygon(self):
        self.polygon_data.object = None
        
    def refresh_polygon(self):
        """reload polygon.spolygon.gtpolygon"""
        self.setPolygon(self.polygon_data.qtpolygon)


    def select_polygon(self):
        """set selected and repaint polygon"""
        if self.state == ItemStates.standart:
            self.state = ItemStates.selected
            self.update_brush()

    def deselect_polygon(self):
        """set unselected and repaint polygon"""
        if self.state == ItemStates.selected:
            self.state = ItemStates.standart
            self.update_brush()

    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        event.gobject = self

    def paint(self, painter, option, widget):
        """Redefinition of standard paint function"""
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self.polygon_data.drawpath)
