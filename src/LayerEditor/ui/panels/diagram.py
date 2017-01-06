"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import ui.data.diagram_structures as struc
from ui.gitems import Line, Point
from ui.gitems import ItemStates
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
        self.operation_state = OperatinState.point
        """Operatoin mode"""
        # added operation        
        self._last_line = None
        """last added shapes"""
        self._last_p1_real = None
        """if first point of last line is real, there is"""
        self._last_p1_on_line = None
        """if first point of last line is real, there is"""
        self._last_counter = 0
        """counter for last line"""
        super(Diagram, self).__init__(parent)        
        self.set_data(data)    
        self.setSceneRect(0, 0, 20, 20)
    
    def _add_point(self, gobject, p1):
        """Add point to diagram and paint it."""
        if gobject is None:
            point = self._data.add_point(p1.x(), p1.y()) 
            p = Point(point,  self._data)
            self.addItem(p)
        elif isinstance(gobject, Point):
            return gobject
        elif isinstance(gobject, Line):                
            point, l2 = self._data.add_point_to_line(gobject.line, p1.x(), p1.y())
            l = Line(l2, self._data)
            self.addItem(l) 
            p = Point(point,  self._data)
            self.addItem(p)                 
        return p
        
    def _add_line(self, gobject, p,  add_last=True):
        """If self._last_line is set, last line is repaint to point p and change 
        its state. If add_last is True new last line is created. if 
        self._last_line is None, self._last_line is added only"""
        if not self._last_line:
            if gobject is None:
                self._last_p1_real = None
                self._last_p1_on_line = None
                px = p.x()
                py = p.y()
            elif isinstance(gobject, Point):
                self._last_p1_real = gobject
                self._last_p1_on_line = None
                px = gobject.x()
                py = gobject.y()
            elif isinstance(gobject, Line):
                self._last_p1_real = None
                self._last_p1_on_line = gobject
                px, py =  struc.Diagram.get_point_on_line(gobject, p.x(), p.y())
        else:
            if self._last_p1_real is not None:
                if isinstance(gobject, Point) and gobject==self._last_p1_real:
                    # line with len==0, ignore 
                    if not add_last:
                        self._last_p1_real = None
                        self._last_p1_on_line = None
                        self._last_line = None
                    return
                p1 = self._last_p1_real               
            else:
                p1 = self._add_point(gobject, QtCore.QPointF(self._last_line.p1.x, self._last_line.p1.y))
            p2 = self._add_point(gobject, p)
            px = p.x()
            py = p.y()            
            line = self._data. join_line(p1.point, p2.point)
            l = Line(line, self._data)
            self.addItem(l) 
            self._last_p1_real = p2
            self._last_p1_on_line = None
            self._remove_last()
        if add_last:                
            line = struc.Diagram.make_tmp_line(px, py, p.x(), p.y())
            p1 = Point(line.p1, self._data)
            p1.set_tmp()
            self.addItem(p1)             
            p2 = Point(line.p2, self._data)
            p2.set_tmp()
            self.addItem(p2) 
            l = Line(line, self._data)
            l.set_tmp()
            self.addItem(l) 
            self._last_line = line
        
    def _shift_last(self, new_p2):
        """Shift point p2 and line (p1,p2) in diagram and repaint it."""
        self._last_line.p2.object.move_point(new_p2)
        
    def _remove_last(self):
        """Remove last point and line from diagram."""
        if self._last_line is not None:
            p1 = self._last_line.p1.object
            p2 = self._last_line.p2.object
            l = self._last_line.object
            p1.release_point()
            self.removeItem(p1)
            p2.release_point()
            self.removeItem(p2)
            self._last_line.object.release_line()
            self.removeItem(l)                        
            self._last_line = None
        
    def set_select_mode(self, selected):
        """Set selection mode"""
        self._selection_mode = selected
        if self._last_line is not None: 
            self.remove_last()
    
    def set_operation_state(self, selected):
        """Set operation state"""
        self.operation_state = selected
        if self._last_line is not None: 
            self.remove_last()
        
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
        elif self._last_line is not None:
            self._last_counter += 1
            if self._last_counter%3==0:
                self._shift_last(event.scenePos()) 
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._point_moving is not None:
            self._point_moving_counter += 1
            if self._point_moving_counter%3==0: 
                if self._point_moving_counter == 3:
                    self._point_moving.move_point(event.scenePos(), ItemStates.moved)
                else:
                    self._point_moving.move_point(event.scenePos())                
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._line_moving is not None:
            self._line_moving_counter += 1
            if self._line_moving_counter%3==0:
                if self._line_moving_counter == 3:
                    self._line_moving.shift_line(event.scenePos()-self._line_moving_pos, ItemStates.moved)
                else:
                    self._line_moving.shift_line(event.scenePos()-self._line_moving_pos)
                self._line_moving_pos = event.scenePos()
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        else:
            self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
    
    def _next_point(self, event):
        """next point in line or point mode is clicked"""
        if self.operation_state is OperatinState.line:
            if event.button()==QtCore.Qt.Qt.LeftButton:
                self._add_line(event.gobject, event.scenePos())            
            elif event.button()==QtCore.Qt.Qt.RightButton:
                self._add_line(event.gobject, event.scenePos(), False)
                
        elif self.operation_state is OperatinState.point:
            if event.gobject is None or not isinstance(event.gobject, Point):
                if event.button()==QtCore.Qt.Qt.LeftButton:
                    self._add_point(event.gobject, event.scenePos())
    
    def mouseReleaseEvent(self,event):
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)
        if self._moving:
            self._moving = False
            if  self._moving_counter>0:
                self._data.x += (self._moving_x-event.screenPos().x())/self._data.zoom
                self._data.y += (self._moving_y-event.screenPos().y())/self._data.zoom
                self.possChanged.emit()
            else:
                if not self._selection_mode:
                    self._next_point(event)                       
        elif self._point_moving is not None:
            if  self._point_moving_counter>0:
                self._point_moving.move_point(event.scenePos(), ItemStates.standart)
            else:
                if not self._selection_mode:
                    self._next_point(event)
            self._point_moving = None
        elif self._line_moving is not None:
            if  self._line_moving_counter>0:
                self._line_moving.shift_line(event.scenePos()-self._line_moving_pos, ItemStates.standart)
            else:
                if not self._selection_mode:
                    self._next_point(event)
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
