import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates, get_state_color
from leconfig import cfg

class Point(QtWidgets.QGraphicsEllipseItem):
    """ 
    Represents a block in the diagram 
    """
    
    STANDART_ZVALUE = 120
    MOVE_ZVALUE = 20
    TMP_ZVALUE = 0
   
    def __init__(self, point, parent=None):
        """if item is selected"""
        self.point = point
        self._tmp = False
        point.object = self
        self.state = ItemStates.standart
        """Item state"""
        super(Point, self).__init__(self.point.x-2/cfg.diagram.zoom, 
            self.point.y-2/cfg.diagram.zoom, 4/cfg.diagram.zoom, 4/cfg.diagram.zoom, parent)   
        self.setPen(cfg.diagram.pen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))    
        self.setZValue(self.STANDART_ZVALUE) 
        
    def set_tmp(self):
        """set style and z"""
        self._tmp = True
        self.state = ItemStates.added
        self.setZValue(self.TMP_ZVALUE) 
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        
    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that change line with accoding zoom"""
        if cfg.diagram.pen.widthF() != self.pen().widthF():
            self.prepareGeometryChange()
            self.setRect(self.point.x-2/cfg.diagram.zoom, 
                self.point.y-2/cfg.diagram.zoom, 4/cfg.diagram.zoom, 4/cfg.diagram.zoom)
            self.setPen(cfg.diagram.pen)
        if self.pen().color()!=get_state_color(self.state):
            pen = QtGui.QPen(cfg.diagram.pen)
            pen.setColor(get_state_color(self.state))
            self.setPen(pen)
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        if self.state==ItemStates.standart:
            color = self.point.get_color()
            if color != "##":
                old_pen = self.pen()
                pen = QtGui.QPen(cfg.diagram.pen)
                pen.setColor(QtGui.QColor(color))
                pen.setStyle(QtCore.Qt.DotLine)
                pen.setWidthF(5*self.pen().widthF())
                self.setPen(pen)
                super(Point, self).paint(painter, option, widget)
                self.setPen(old_pen)
        super(Point, self).paint(painter, option, widget)
        
    def move_point(self, pos=None, new_state=None):
        """Move point to new pos and move all affected lines"""
        if new_state is not None:
            self.state = new_state
            if new_state is ItemStates.moved:
                self.setZValue(self.MOVE_ZVALUE)
                self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
                self.ungrabMouse()
            else:
                self.setZValue(self.STANDART_ZVALUE)
                self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) 
        if pos is not None:
            self.point.x = pos.x()
            self.point.y = pos.y()
        self.setRect(self.point.x-2/cfg.diagram.zoom, 
            self.point.y-2/cfg.diagram.zoom, 4/cfg.diagram.zoom, 4/cfg.diagram.zoom) 
        for line in self.point.lines:
            line.object.move_line(new_state)
            
    def shift_point(self, shift, new_state=None):
        """Move point to new pos and move all affected lines"""        
        pos = QtCore.QPointF(self.point.x, self.point.y) + shift
        self.move_point(pos, new_state)
        
    def select_point(self):
        """set selected and repaint point"""
        if self.state==ItemStates.standart:
            self.state = ItemStates.selected
            self.update()
        
    def deselect_point(self):
        """set unselected and repaint point"""
        if self.state==ItemStates.selected:
            self.state = ItemStates.standart
            self.update()
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Point, self).mousePressEvent(event)
        else:
            event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Point, self).mouseReleaseEvent(event)
        else:
            event.gobject = self
        
    def release_point(self):
        self.point.object = None
