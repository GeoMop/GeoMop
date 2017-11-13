import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates
from leconfig import cfg

class Polygon(QtWidgets.QGraphicsPolygonItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    MIN_ZVALUE = -999
    DEFAUT_COLOR = "#f0f0e8"
    
    def __init__(self, polygon, parent=None):
        super(Polygon, self).__init__(polygon.qtpolygon)
        self.polygon = polygon 
        polygon.object = self
        """polygon data object"""
        self.state = ItemStates.standart
        """Item state"""
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.color = polygon.get_color()
        self.depth = polygon.depth
        #self.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor))
        self.setZValue(self.MIN_ZVALUE+self.depth)

        # last brush parameters
        self.last_brush_zoom = cfg.diagram.recount_zoom
        self.last_brush_color = self.color
        self.last_brush_state = self.state

        self.update_brush()
        
    def paint(self, painter, option, widget):
        """Redefination of standart paint function"""
        if cfg.diagram.recount_zoom != self.last_brush_zoom or \
                self.color != self.last_brush_color or \
                self.state != self.last_brush_state:
            self.update_brush()
        super().paint(painter, option, widget)

    def update_color(self):
        color = self.polygon.get_color()
        if self.color != color:
            self.color = color
            self.update()
            
    def update_depth(self):
        """Check and set polygon depth"""
        if self.depth != self.polygon.depth:
            self.depth = self.polygon.depth
            self.setZValue(self.MIN_ZVALUE+self.depth)

    def update_brush(self):
        if self.state == ItemStates.selected:
            brush = QtGui.QBrush(cfg.diagram.brush_selected)
        else:
            brush = QtGui.QBrush(cfg.diagram.brush)

        if self.color == "##":
            color = self.DEFAUT_COLOR
        else:
            color = self.color
        brush.setColor(QtGui.QColor(color))
        self.setBrush(brush)

        self.last_brush_zoom = cfg.diagram.recount_zoom
        self.last_brush_color = self.color
        self.last_brush_state = self.state

    def release_polygon(self):
        self.polygon.object = None
        
    def refresh_polygon(self):
        """reload polygon.spolygon.gtpolygon"""
        self.setPolygon(self.polygon.qtpolygon)

    def select_polygon(self):
        """set selected and repaint polygon"""
        if self.state == ItemStates.standart:
            self.state = ItemStates.selected
            self.update()

    def deselect_polygon(self):
        """set unselected and repaint polygon"""
        if self.state == ItemStates.selected:
            self.state = ItemStates.standart
            self.update()

    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        event.gobject = self
