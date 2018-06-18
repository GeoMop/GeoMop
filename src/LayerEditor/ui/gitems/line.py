import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .states import ItemStates, get_state_color
from LayerEditor.leconfig import cfg
from LayerEditor import definitions

class Line(QtWidgets.QGraphicsLineItem):
    """ 
        Represents a join of nodes in the diagram
    """

    DASH_PATTERN = [10, 5]
    DASH_PATTERN_BOLD = [5, 2.5]
    
    def __init__(self, line_data, parent=None, tmp=False):
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
        self.setZValue(definitions.ZVALUE_LINE)
        self.bold = False
        if tmp:
            self.set_tmp()
        self.update_color()

    def set_tmp(self):
        """set style and z"""
        self._tmp = True
        self.state = ItemStates.added
        self.setZValue(definitions.ZVALUE_LINE_TMP)
        #self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def paint(self, painter, option, widget):
        """Redefinition of standard paint function"""
        # don't paint if line is null line
        if self.line().isNull():
            return

        painter.setRenderHints(painter.renderHints() | QtGui.QPainter.Antialiasing)
        painter.setPen(self.real_pen)
        painter.drawLine(self.line())

    def set_width(self):
        """Set line width according to actual zoom"""
        if self.bold:
            self.real_pen.setWidthF(3 * cfg.diagram.pen.widthF())
        else:
            self.real_pen.setWidthF(cfg.diagram.pen.widthF())
        self.update()

    def update_geometry(self):
        """Update geometry according to actual zoom"""
        self.set_width()
        self.setPen(cfg.diagram.no_pen)

    def update_color(self):
        """Update color to actual color"""
        style = QtCore.Qt.SolidLine
        if self.state == ItemStates.selected or self.state == ItemStates.moved:
            style = QtCore.Qt.CustomDashLine
        self.real_pen.setStyle(style)
        if style == QtCore.Qt.CustomDashLine:
            self.real_pen.setDashPattern(self.DASH_PATTERN)

        color = get_state_color(self.state)
        self.bold = False
        if self.state != ItemStates.added:
            c = self.line_data.get_color()
            if c != "##":
                color =  QtGui.QColor(c)
                self.bold = True
                if style == QtCore.Qt.CustomDashLine:
                    self.real_pen.setDashPattern(self.DASH_PATTERN_BOLD)
        self.real_pen.setColor(QtGui.QColor(color))
        self.set_width()

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
            self.update_color()

    def deselect_line(self):
        """set unselected and repaint line"""
        if self.state==ItemStates.selected:
            self.state = ItemStates.standart
            self.update_color()

    def move_line(self, new_state=None):
        """Move line"""
        if new_state is not None:
            self.state = new_state
            if new_state is ItemStates.moved:
                self.setZValue(definitions.ZVALUE_LINE_MOVE)
                #self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
            else:
                self.setZValue(definitions.ZVALUE_LINE)
                self.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor)) 
        self.setLine(self.line_data.p1.x, self.line_data.p1.y, self.line_data.p2.x, self.line_data.p2.y)
        self.update_color()
        
    def shift_line(self, shift, new_state=None):
        """shift line"""
        self.line_data.p1.object.shift_point(shift, new_state, False)
        self.line_data.p2.object.shift_point(shift, new_state, False)
        
    def release_line(self):
        self.line_data.object = None
