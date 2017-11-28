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
    TMP_ZVALUE = 1
    POINT_SIZE = 4
    POINT_BOLD_SIZE = 6

    white_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.white))
   
    def __init__(self, point_data, parent=None):
        """if item is selected"""
        self.point_data = point_data
        self._tmp = False
        point_data.object = self
        self.state = ItemStates.standart
        """Item state"""
        self.bold = False
        super().__init__()
        self.set_size()
        self.setPen(cfg.diagram.pen)
        self.setBrush(QtGui.QBrush(self.pen().color()))
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))    
        self.setZValue(self.STANDART_ZVALUE)

    def set_size(self):
        """Set point size according to actual zoom"""
        ps = self.POINT_SIZE
        if self.bold:
            ps = self.POINT_BOLD_SIZE
        self.setRect(self.point_data.x - ps / cfg.diagram.zoom,
                     self.point_data.y - ps / cfg.diagram.zoom,
                     2 * ps / cfg.diagram.zoom,
                     2 * ps / cfg.diagram.zoom)

    def set_tmp(self):
        """set style and z"""
        self._tmp = True
        self.state = ItemStates.added
        self.setZValue(self.TMP_ZVALUE) 
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        
    def paint(self, painter, option, widget):
        """Redefination of standart paint function, that change line with accoding zoom"""
        # size
        bold = False
        if self.state != ItemStates.added and self.point_data.get_color() != "##":
            bold = True
        if cfg.diagram.pen.widthF() != self.pen().widthF() or bold != self.bold:
            self.bold = bold
            self.set_size()
            self.setPen(cfg.diagram.pen)
            self.setBrush(QtGui.QBrush(self.pen().color()))

        # color
        color = get_state_color(self.state)
        if self.state != ItemStates.added:
            c = self.point_data.get_color()
            if c != "##":
                color = c
        if self.pen().color() != color:
            pen = QtGui.QPen(cfg.diagram.pen)
            pen.setColor(QtGui.QColor(color))
            self.setPen(pen)
            brush = self.brush()
            brush.setColor(pen.color())
            self.setBrush(brush)

        # paint
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        if self.state == ItemStates.selected or self.state == ItemStates.moved:
            painter.setPen(self.pen())
            painter.setBrush(self.white_brush)
            painter.drawRect(self.rect())
        else:
            super().paint(painter, option, widget)

        # if cfg.diagram.pen.widthF() != self.pen().widthF():
        #     self.prepareGeometryChange()
        #     self.setRect(self.point.x-2/cfg.diagram.zoom,
        #         self.point.y-2/cfg.diagram.zoom, 4/cfg.diagram.zoom, 4/cfg.diagram.zoom)
        #     self.setPen(cfg.diagram.pen)
        # if self.pen().color()!=get_state_color(self.state):
        #     pen = QtGui.QPen(cfg.diagram.pen)
        #     pen.setColor(get_state_color(self.state))
        #     self.setPen(pen)
        # painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        # if self.state==ItemStates.standart:
        #     color = self.point.get_color()
        #     if color != "##":
        #         old_pen = self.pen()
        #         pen = QtGui.QPen(cfg.diagram.pen)
        #         pen.setColor(QtGui.QColor(color))
        #         pen.setStyle(QtCore.Qt.DotLine)
        #         pen.setWidthF(5*self.pen().widthF())
        #         self.setPen(pen)
        #         super(Point, self).paint(painter, option, widget)
        #         self.setPen(old_pen)
        # super(Point, self).paint(painter, option, widget)
        
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
            self.point_data.x = pos.x()
            self.point_data.y = pos.y()
            self.set_size()
        for line in self.point_data.lines:
            line.object.move_line(new_state)
            
    def shift_point(self, shift, new_state=None):
        """Move point to new pos and move all affected lines"""        
        pos = QtCore.QPointF(self.point_data.x, self.point_data.y) + shift
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
        self.point_data.object = None
