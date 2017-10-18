import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates, get_state_color
from leconfig import cfg

class Line(QtWidgets.QGraphicsLineItem):
    """ 
        Represents a join of nodes in the diagram
    """
    
    STANDART_ZVALUE = 110
    MOVE_ZVALUE = 10
    TMP_ZVALUE = 0
    
    def __init__(self, line, parent=None):
        super(Line, self).__init__(line.p1.x, line.p1.y, line.p2.x, line.p2.y, parent)
        self.line = line
        self._tmp = False
        line.object = self
        """Line data object"""
        self.state = ItemStates.standart
        """Item state"""
        self.setPen(cfg.diagram.pen)
        self.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor))
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
            self.setPen(cfg.diagram.pen)
        if self.pen().color()!=get_state_color(self.state):
            pen = QtGui.QPen(cfg.diagram.pen)
            pen.setColor(get_state_color(self.state))
            self.setPen(pen)            
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing) 
        super(Line, self).paint(painter, option, widget)            
        if self.state==ItemStates.standart:
            color = self.line.get_color()
            if color != "#000000":
                old_pen = self.pen()
                pen = QtGui.QPen(cfg.diagram.pen)
                pen.setColor(QtGui.QColor(color))
                pen.setStyle(QtCore.Qt.DotLine)
                pen.setWidthF(1.5*self.pen().widthF())
                self.setPen(pen)
                super(Line, self).paint(painter, option, widget)
                self.setPen(old_pen)
        
        
    def mousePressEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Line, self).mousePressEvent(event)
        else:
            event.gobject = self
        
    def mouseReleaseEvent(self,event):
        """Standart mouse event"""
        if self._tmp:
            super(Line, self).mouseReleaseEvent(event)
        else:
            event.gobject = self
            
    def refresh_line(self):
        """Refresh line after point changes"""
        self.setLine(self.line.p1.x, self.line.p1.y, self.line.p2.x, self.line.p2.y)
            
    def select_line(self):
        """set selected and repaint line"""
        if self.state==ItemStates.standart:
            self.state = ItemStates.selected
            self.update()
        
    def deselect_line(self):
        """set unselected and repaint line"""
        if self.state==ItemStates.selected:
            self.state = ItemStates.standart
            self.update()
        
    def move_line(self, new_state=None):
        """Move line"""
        if new_state is not None:
            self.state = new_state
            if new_state is ItemStates.moved:
                self.setZValue(self.MOVE_ZVALUE)
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor)) 
            else:
                self.setZValue(self.STANDART_ZVALUE)
                self.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor)) 
        self.setLine(self.line.p1.x, self.line.p1.y, self.line.p2.x, self.line.p2.y)
        
    def shift_line(self, shift, new_state=None):
        """shift line"""
        self.line.p1.object.shift_point(shift, new_state)
        self.line.p2.object.shift_point(shift, new_state)
        
    def release_line(self):
        self.line.object = None
