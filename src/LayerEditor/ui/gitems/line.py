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
    DASH_PATTERN = [10, 5]
    DASH_PATTERN_BOLD = [5, 2.5]
    
    def __init__(self, line_data, parent=None):
        super().__init__(line_data.p1.x, line_data.p1.y, line_data.p2.x, line_data.p2.y, parent)
        self.line_data = line_data
        self._tmp = False
        line_data.object = self
        """Line data object"""
        self.state = ItemStates.standart
        """Item state"""
        self.setPen(cfg.diagram.no_pen)
        self.real_pen = QtGui.QPen(cfg.diagram.pen)
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
        # don't paint if line is null line
        if self.line().isNull():
            return

        # width
        if cfg.diagram.pen.widthF() != self.real_pen.widthF():
            self.real_pen = QtGui.QPen(cfg.diagram.pen)
            self.setPen(cfg.diagram.no_pen)

        # color
        color = get_state_color(self.state)
        if self.state != ItemStates.added:
            c = self.line_data.get_color()
            if c != "##":
                color = c
        if self.real_pen.color() != color:
            self.real_pen = QtGui.QPen(cfg.diagram.pen)
            self.real_pen.setColor(QtGui.QColor(color))

        # style
        style = QtCore.Qt.SolidLine
        if self.state == ItemStates.selected or self.state == ItemStates.moved:
            style = QtCore.Qt.CustomDashLine
        if self.real_pen.style() != style:
            self.real_pen.setStyle(style)
            if style == QtCore.Qt.CustomDashLine:
                self.real_pen.setDashPattern(self.DASH_PATTERN)

        # bold
        if self.state != ItemStates.added and self.line_data.get_color() != "##":
            self.real_pen.setWidthF(3*self.real_pen.widthF())
            if style == QtCore.Qt.CustomDashLine:
                self.real_pen.setDashPattern(self.DASH_PATTERN_BOLD)

        # paint
        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        painter.setPen(self.real_pen)
        painter.drawLine(self.line())

        # if cfg.diagram.pen.widthF() != self.pen().widthF():
        #     self.setPen(cfg.diagram.pen)
        # if self.pen().color()!=get_state_color(self.state):
        #     pen = QtGui.QPen(cfg.diagram.pen)
        #     pen.setColor(get_state_color(self.state))
        #     self.setPen(pen)
        # painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        # super(Line, self).paint(painter, option, widget)
        # if self.state==ItemStates.standart:
        #     color = self.line.get_color()
        #     if color != "##":
        #         old_pen = self.pen()
        #         pen = QtGui.QPen(cfg.diagram.pen)
        #         pen.setColor(QtGui.QColor(color))
        #         pen.setStyle(QtCore.Qt.DotLine)
        #         pen.setWidthF(1.5*self.pen().widthF())
        #         self.setPen(pen)
        #         super(Line, self).paint(painter, option, widget)
        #         self.setPen(old_pen)
        
        
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
        self.setLine(self.line_data.p1.x, self.line_data.p1.y, self.line_data.p2.x, self.line_data.p2.y)
            
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
        self.setLine(self.line_data.p1.x, self.line_data.p1.y, self.line_data.p2.x, self.line_data.p2.y)
        
    def shift_line(self, shift, new_state=None):
        """shift line"""
        self.line_data.p1.object.shift_point(shift, new_state, False)
        self.line_data.p2.object.shift_point(shift, new_state, False)
        
    def release_line(self):
        self.line_data.object = None
