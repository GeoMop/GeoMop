"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from ui.gitems import Line, Point
from enum import IntEnum


class OperatinState(IntEnum):
    """Diagram Operations states"""
    line = 0
    point = 1
    
    
class Diagram(QtWidgets.QGraphicsScene):
    """
    GeoMop design area
    
    pyqtSignals:
        * :py:attr:`cursorChanged(float, float) <cursorChanged>`
        * :py:attr:`possChanged() <possChanged>`
    """
    cursorChanged = QtCore.pyqtSignal(float, float)
    """Signal is sent when cursor position has changed.

    :param int line: new x coordinate
    :param int column: new y coordinate
    """
    possChanged = QtCore.pyqtSignal()
    """
    Signal is sent, when zoom has changed or vissible part of scene is move. 
    New coordinates is set in _data variable and parent view should connect
    to signal and change visualisation.
    """

    def __init__(self, data, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        self._data = data
        """Diagram data"""
        # move point variables
        self._point_moving = None
        """point is drawn"""
        self._point_moving_counter = 0
        """counter for moving"""
        # move line variables
        self._line_moving = None
        """point is drawn"""
        self._line_moving_counter = 0
        """counter for moving"""
        self._line_moving_pos = None
        """last coordinates for line moving"""        
        # move canvas variables
        self._moving = False
        """scene is drawn"""
        self._moving_x = 0
        """last x-coordinates for moving"""
        self._moving_y = 0
        """last y-coordinates for moving"""
        self._moving_counter = 0
        """counter for moving"""
        # zoom variables
        self._recount_zoom = 1
        """zoom affected displayed items"""        
        self._selection_mode = False        
        """Diagram is in selection mode"""
        self.operatoin_state = OperatinState.point
        """Operatoin mode"""
        super(Diagram, self).__init__(parent)        
        self.set_data(data)    
        self.setSceneRect(0, 0, 20, 20)
        
    def set_select_mode(self, selected):
        """Set selection mode"""
        self._selection_mode = selected
    
    def set_operation_state(self, selected):
        """Set operation state"""
        self.operatoin_state = selected 
        
    def set_data(self, data):
        self._data = data
        self.clear()
        for line in data.lines:
            l = Line(line,  self._data)
            self.addItem(l) 
        for point in data.points:
            p = Point(point,  self._data)
            self.addItem(p)
        self._recount_zoom = self._data.zoom
            
    def mouseMoveEvent(self, event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)        
        if self._moving: 
            self._moving_counter += 1
            if self._moving_counter%3==0:
                self._data.x += (self._moving_x-event.screenPos().x())/self._data.zoom
                self._data.y += (self._moving_y-event.screenPos().y())/self._data.zoom
                self._moving_x = event.screenPos().x()
                self._moving_y = event.screenPos().y()
                self.possChanged.emit()
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._point_moving is not None:
            self._point_moving_counter += 1
            if self._point_moving_counter%3==0:                
                self._point_moving.move_point(event.scenePos())                
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._line_moving is not None:
            self._line_moving_counter += 1
            if self._line_moving_counter%3==0:
                self._line_moving.shift_line(event.scenePos()-self._line_moving_pos)
                self._line_moving_pos = event.scenePos()
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        else:
            self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        
    def mouseReleaseEvent(self,event):
        if self._moving:
            self._data.x += (self._moving_x-event.screenPos().x())/self._data.zoom
            self._data.y += (self._moving_y-event.screenPos().y())/self._data.zoom
            self.possChanged.emit()
            self._moving = False
        if self._point_moving is not None:
            if  self._point_moving_counter>0:
                self._point_moving.move_point(event.scenePos())
            self._point_moving = None
        if self._line_moving is not None:
            if  self._line_moving_counter>0:
                self._line_moving.shift_line(event.scenePos()-self._line_moving_pos)
            self._line_moving = None    
            
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self). mousePressEvent(event)
        if self._moving:
            # fix bad state
            self.possChanged.emit()
            self._moving = False
            if event.gobject is None:
                return
        if event.gobject is None:
            self._moving_counter = 0
            self._moving = True
            self._moving_x = event.screenPos().x()
            self._moving_y = event.screenPos().y()
        else:
            if isinstance(event.gobject, Line):
                self._line_moving_counter = 0
                self._line_moving = event.gobject
                self._line_moving_pos = event.scenePos()
            else:
                # point
                self._point_moving_counter = 0
                self._point_moving = event.gobject

    def wheelEvent(self, event):
        """wheel event for zooming"""
        if self._data is None:
            return
        delta = event.delta()/3000
        if delta>0.1:
            delta = 0.1
        if delta<-0.1:
            delta = -0.1        
        # repair possition
        self._data.x +=  (event.scenePos().x() -  self._data.x) * delta
        self._data.y += (event.scenePos().y() - self._data.y) * delta
        # repair zoom
        self._data.zoom *= (1.0 + delta)
        # send signal
        self.possChanged.emit()
