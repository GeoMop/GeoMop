"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import ui.data.diagram_structures as struc
from ui.gitems import Line, Point, ShpBackground, DiagramView, Blink, Polygon
from ui.gitems import ItemStates
from leconfig import cfg
    
class Diagram(QtWidgets.QGraphicsScene):
    """
    GeoMop Layer Editor design area
    
    Y coordinetes is negativ for right map orientation. For displying or setting 
    is need set opposite value.
    
    pyqtSignals:
        * :py:attr:`cursorChanged(float, float) <cursorChanged>`
        * :py:attr:`possChanged() <possChanged>`
        * :py:attr:`regionUpdateRequired(int, int) <regionUpdateRequired>`
    """
    cursorChanged = QtCore.pyqtSignal(float, float)
    """Signal is sent when cursor position has changed.

    :param float line: new x coordinate
    :param float column: new y coordinate
    """
    possChanged = QtCore.pyqtSignal()
    """
    Signal is sent, when zoom has changed or vissible part of scene is move. 
    New coordinates is set in _data variable and parent view should connect
    to signal and change visualisation.
    """
    regionUpdateRequired = QtCore.pyqtSignal(int, int)
    """
    Shape was clicked and region update in region panel is required
    
    :param int dimension: shape dimension
    :param int idx: shape index in diagram structure
    """
    BLINK_INTERVAL = 500
    """blink interval in ms"""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        # move point variables
        self._point_moving = None
        """point is drawn"""
        self._point_moving_counter = 0
        """counter for moving"""
        self._point_moving_old = None
        """Old point position"""        
        # move line variables
        self._line_moving = None
        """point is drawn"""
        self._line_moving_counter = 0
        """counter for moving"""
        self._line_moving_pos = None        
        """last coordinates for line moving"""        
        self._line_moving_old = None
        """Old line position"""
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
        # added operation        
        self._last_line = None
        """last added shapes"""
        self._last_p1_real = None
        """if first point of last line is real, there is"""
        self._last_p1_on_line = None
        """if first point of last line is real, there is"""
        self._last_counter = 0
        """counter for last line"""
        # selected operation
        self._selected_points = []
        """list of selected points"""
        self._selected_lines = []
        """list of selected lines"""
        # control object
        self._control_object = None
        """object, that is below cursor, if button press event is emited"""
        #blink
        self.blink = None
        """blink object"""
        self.blink_timer = QtCore.QTimer()
        """Blink timer"""
        self.blink_timer.setSingleShot(True) 
        
        super(Diagram, self).__init__(parent)
        self.blink_timer.timeout.connect(self.blink_end)
        self.blink_timer.start(self.BLINK_INTERVAL) 
  
        self.set_data()    
        self.setSceneRect(0, 0, 20, 20)
        
    def refresh_shp_backgrounds(self):
        """refresh updated shape files on background"""
        for shp in cfg.diagram.shp.datas:
            if shp.shpdata.object is None:
                s = ShpBackground(shp.shpdata, shp.color)
                self.addItem(s) 
               # s.prepareGeometryChange()
                shp.refreshed = True
            elif not shp.refreshed:
                shp.shpdata.object.color = shp.color
                shp.shpdata.object.update()
                shp.refreshed = True
    
    def _add_point(self, gobject, p1, label='Add point'):
        """Add point to diagram and paint it."""
        if gobject is None or isinstance(gobject, Polygon):
            point =cfg.diagram.add_point(p1.x(), p1.y(), label) 
            p = Point(point)
            self.addItem(p)
        elif isinstance(gobject, Point):
            return gobject, label
        elif isinstance(gobject, Line): 
            if label=='Add point':
                label='Add new point to line'
            point, l2 = cfg.diagram.add_new_point_to_line(gobject.line, p1.x(), p1.y(), label)
            l = Line(l2)
            self.addItem(l) 
            p = Point(point)
            self.addItem(p)
            self._add_polygons()
        return p, None
        
    def _add_polygons(self):
        """If is new polygon in data object, created it"""
        if len(cfg.diagram.new_polygons)>0:
            for polygon in cfg.diagram.new_polygons:
                p = Polygon(polygon)
                self.addItem(p)  
            cfg.diagram.new_polygons = []
            
    def _del_polygons(self):
        """If is new polygon in data object, created it"""
        if len(cfg.diagram.deleted_polygons)>0:
            for polygon in cfg.diagram.deleted_polygons:
                obj = polygon.object
                obj.release_polygon()
                self.removeItem(obj)
            cfg.diagram.deleted_polygons = []
            
    def _add_line(self, gobject, p,  add_last=True):
        """If self._last_line is set, last line is repaint to point p and change 
        its state. If add_last is True new last line is created. if 
        self._last_line is None, self._last_line is added only"""
        if not self._last_line:
            if gobject is None or isinstance(gobject, Polygon):
                self._last_p1_real = None
                self._last_p1_on_line = None
                px = p.x()
                py = p.y()
            elif isinstance(gobject, Point):
                self._last_p1_real = gobject
                self._last_p1_on_line = None
                px = gobject.point.x
                py = gobject.point.y
            elif isinstance(gobject, Line):
                self._last_p1_real = None
                self._last_p1_on_line = gobject
                px, py =  struc.Diagram.get_point_on_line(gobject.line, p.x(), p.y())
        else:
            label = "Add line"
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
                p1, label = self._add_point(self._last_p1_on_line, 
                    QtCore.QPointF(self._last_line.p1.x, self._last_line.p1.y), label)
            p2, label = self._add_point(gobject, p, label)
            px = p.x()
            py = p.y()
            added_points, moved_points, added_lines = cfg.diagram.join_line_intersection(
                p1.point, p2.point, label)
            self.update_changes(added_points, [], moved_points, added_lines, [])            
            self._last_p1_real = p2
            self._last_p1_on_line = None
            self._remove_last()
        if add_last:                
            line = struc.Diagram.make_tmp_line(px, py, p.x(), p.y())
            p1 = Point(line.p1)
            p1.set_tmp()
            self.addItem(p1)             
            p2 = Point(line.p2)
            p2.set_tmp()
            self.addItem(p2) 
            l = Line(line)
            l.set_tmp()
            self.addItem(l) 
            self._last_line = line
            self._add_polygons()
        
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
            self._del_polygons()
    
    def update_changes(self, added_points, removed_points, moved_points, added_lines, removed_lines):
        for point in added_points:
            p = Point(point)
            self.addItem(p)
        for line in added_lines:
            l = Line(line)
            self.addItem(l)        
        for point in removed_points:
            p = point.object
            p.release_point()
            self.removeItem(p)
        for line in removed_lines:
            l = line.object
            l.release_line()
            self.removeItem(l)
        for point in moved_points:
            point.object.move_point()        
        self._add_polygons()
        self._del_polygons()
        
    def release_views(self):
        """release all diagram views"""
        deleted = []
        for uid, view in cfg.diagram.views_object.items():
            deleted.append(view)
        cfg.diagram.views_object = {}
        while len(deleted)>0:
            self.removeItem(deleted.pop())            
        
    def update_views(self):
        """update all diagram views"""
        curr_uid = cfg.diagram.uid
        del_uid = []
        for uid, view in cfg.diagram.views_object.items():            
            if curr_uid==uid or uid not in cfg.diagram.views:
                if uid in cfg.diagram.views_object:
                    del_uid.append(uid)
        for uid in del_uid:
            obj = cfg.diagram.views_object[uid]
            obj.release_view()
            self.removeItem(obj)   
        for uid in cfg.diagram.views:
            if curr_uid!=uid and uid not in cfg.diagram.views_object:    
                view = DiagramView(uid)
                self.addItem(view)
        
    def release_data(self, old_diagram):
        """release all shapes data"""
        for line in cfg.diagrams[old_diagram].lines:
            obj = line.object
            obj.release_line()
            self.removeItem(obj)
        for point in cfg.diagrams[old_diagram].points:
            obj = point.object
            obj.release_point()
            self.removeItem(obj)
        for polygon in cfg.diagrams[old_diagram].polygons:
            obj = polygon.object
            obj.release_polygon()
            self.removeItem(obj)
            
        
    def set_data(self):        
        """set new shapes data"""
        for line in cfg.diagram.lines:
            l = Line(line)
            self.addItem(l) 
        for point in cfg.diagram.points:
            p = Point(point)
            self.addItem(p)
            for polygon in cfg.diagram.polygons:
                if polygon.object is None:
                    p = Polygon(polygon)
                    self.addItem(p)  
        self._recount_zoom = cfg.diagram.zoom
        self._add_polygons()
        
    def blink_start(self, rect):
        """Start blink window"""
        self.blink = Blink(rect)
        self.addItem(self.blink)
        self.blink_timer.start(self.BLINK_INTERVAL)
        
    def blink_end(self):
        """Finish blink window"""
        if self.blink is not None:
            self.removeItem(self.blink)        
        self.blink = None
            
    def mouseMoveEvent(self, event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)
        if self._moving: 
            self._moving_counter += 1
            if self._moving_counter%3==0:
                cfg.diagram.x += (self._moving_x-event.screenPos().x())/cfg.diagram.zoom
                cfg.diagram.y += (self._moving_y-event.screenPos().y())/cfg.diagram.zoom
                self._moving_x = event.screenPos().x()
                self._moving_y = event.screenPos().y()
                self.possChanged.emit()
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._last_line is not None:
            self._last_counter += 1
            if self._last_counter%3==0:
                self._last_line.p2.object.move_point(event.scenePos())                
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
    
    def _select_point(self, point):
        """set point as selected"""
        if not point in self._selected_points:
            self._selected_points.append(point)
            point.select_point()
        else:
            self._selected_points.remove(point)
            point.deselect_point()
    
    def _select_line(self, line, with_points):
        """set line as selected"""
        if not line in self._selected_lines:
            self._selected_lines.append(line)
            line.select_line()        
            if with_points:
                if not line.line.p1.object in self._selected_points:
                    self._select_point(line.line.p1.object)
                if not line.line.p2.object in self._selected_points:
                    self._select_point(line.line.p2.object)
        else:
            self._selected_lines.remove(line)
            line.deselect_line()
            if with_points:
                if line.line.p1.object in self._selected_points:
                    self._deselect_point(line.line.p1.object)
                if not line.line.p2.object in self._selected_points:
                    self._deselect_point(line.line.p2.object)
        
    def delete_selected(self):
        """delete selected"""
        first = True
        for line in self._selected_lines:
            l = line.line
            line.release_line()
            self.removeItem(line)
            if first:
                cfg.diagram.delete_line(l, "Delete selected")
                first = False
            else:
                cfg.diagram.delete_line(l, None)
        self._selected_lines = []
        removed = []
        for point in self._selected_points:            
            p = point.point
            if first:
                label = "Delete selected"
                first = False
            else:
                label = None
            if cfg.diagram.try_delete_point(p, label):
                point.release_point()
                self.removeItem(point)
                removed.append(point)
        for point in removed:
            self._selected_points.remove(point)
        self._del_polygons()       
    
    def select_all(self): 
        """select all items"""
        for line in cfg.diagram.lines:
            self._select_line(line.object, False)
        for point in cfg.diagram.points:
            self._select_point(point.object)
    
    def deselect_selected(self):
        """deselect all items"""
        for line in self._selected_lines:
           line.deselect_line()
        for point in self._selected_points:
            point.deselect_point()
        self._selected_points = []
        self._selected_lines = []
        
    def _anchor_moved_point(self, event):
        """Test if point colide with other and move it"""
        below_item = self.itemAt(event.scenePos(), QtGui.QTransform())        
        if below_item==self._point_moving:
            # moved point with small zorder value is below cursor             
            self._point_moving.move_point(event.scenePos(), ItemStates.standart)
            cfg.diagram.move_point_after(self._point_moving.point, 
                self._point_moving_old.x(), self._point_moving_old.y())
        elif isinstance(below_item, Line):
            cfg.diagram.move_point_after(self._point_moving.point,self._point_moving_old.x(), 
                self._point_moving_old.y(), 'Move point to Line')
            new_line, merged_lines = cfg.diagram.add_point_to_line(below_item.line, 
                self._point_moving.point, None)
            l = Line(new_line)
            self.addItem(l) 
            self._point_moving.move_point(QtCore.QPointF(
                self._point_moving.point.x, self._point_moving.point.y), ItemStates.standart)
            self.update_changes([], [],  [], [], merged_lines)
        elif isinstance(below_item, Point):
            cfg.diagram.move_point_after(self._point_moving.point,self._point_moving_old.x(), 
                self._point_moving_old.y(), 'Merge points')
            removed_lines = cfg.diagram.merge_point(below_item.point, self._point_moving.point, None)
            self._point_moving.release_point()
            self.removeItem(self._point_moving)
            self.update_changes([], [],  [], [], removed_lines)            
            below_item.move_point(event.scenePos(), ItemStates.standart)
        else:
            self._point_moving.move_point(event.scenePos(), ItemStates.standart)
        self.update_related_diagrams(self._point_moving)
            
    def update_related_diagrams(self, points):
        """Update all polynoms related to set points"""
        polygons =  []
        for point in cfg.diagram.points:
            for line in point.lines:
                if line.polygon1 is not None:
                    if not line.polygon1 in polygons:
                        polygons.append(line.polygon1)
                        if line.polygon2 is not None:
                            if not line.polygon2 in polygons:
                                polygons.append(line.polygon2)
        for polygon in polygons:
            polygon.refresh(cfg.diagram)
            
    def mouseReleaseEvent(self,event):
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)
        end_moving = False
        if self._moving:
            self._moving = False
            if  self._moving_counter>1:
                cfg.diagram.x += (self._moving_x-event.screenPos().x())/cfg.diagram.zoom
                cfg.diagram.y += (self._moving_y-event.screenPos().y())/cfg.diagram.zoom
                self.possChanged.emit()
                end_moving = True
        if event.button()==QtCore.Qt.RightButton and \
            event.modifiers()==QtCore.Qt.NoModifier:
            if self._point_moving is not None:
                if  self._point_moving_counter>1:
                    self._anchor_moved_point(event)                    
                else:
                    self._add_line(event.gobject, event.scenePos())           
                self._point_moving = None
            elif self._line_moving is not None:
                if  self._line_moving_counter>1:
                    self._line_moving.shift_line(event.scenePos()-self._line_moving_pos, ItemStates.standart)
                else:
                    self._add_line(event.gobject, event.scenePos())
                self._line_moving = None
            else:
                self._add_line(event.gobject, event.scenePos())
        if event.button()==QtCore.Qt.RightButton and \
            event.modifiers()==QtCore.Qt.ControlModifier:
            if self._last_line is not None:                 
                self._add_line(event.gobject, event.scenePos(), False)                
            else:
                self._add_point(event.gobject, event.scenePos())
                
        if event.button()==QtCore.Qt.LeftButton:
            if event.modifiers()==QtCore.Qt.NoModifier and not end_moving:
                self.deselect_selected()
                if event.gobject is not None:
                    if isinstance(event.gobject, Line):
                        self._select_line(event.gobject, True)
                    elif isinstance(event.gobject, Point):
                        self._select_point(event.gobject)
            if event.modifiers()==QtCore.Qt.ShiftModifier:
                if event.gobject is not None:
                    if isinstance(event.gobject, Line):
                        self._select_line(event.gobject, True)
                    elif isinstance(event.gobject, Point):
                        self._select_point(event.gobject)
            if event.modifiers()==QtCore.Qt.ControlModifier:
                if event.gobject is not None:
                    if isinstance(event.gobject, Polygon):
                        event.gobject.polygon.set_current_region()
                        event.gobject.update_color()
            if event.modifiers()==(QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                if event.gobject is not None:
                    if isinstance(event.gobject, Polygon):
                        self.regionUpdateRequired.emit(2, cfg.diagram.polygons.index(event.gobject.polygon))
                
            
    def mousePressEvent(self,event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self). mousePressEvent(event)
        self._control_object = event.gobject
        if self._moving:
            # fix bad state
            self.possChanged.emit()
            self._moving = False
            if event.gobject is None:
                return
        if event.button()==QtCore.Qt.LeftButton and \
            event.modifiers()==QtCore.Qt.NoModifier:
            self._moving_counter = 0
            self._moving = True
            self._moving_x = event.screenPos().x()
            self._moving_y = event.screenPos().y()                
        if event.button()==QtCore.Qt.RightButton and \
            event.modifiers()==QtCore.Qt.NoModifier:
            if event.gobject is not None:
                if isinstance(event.gobject, Line):
                    self._line_moving_counter = 0
                    self._line_moving = event.gobject
                    self._line_moving_pos = event.scenePos()
                    self._line_moving_old = event.gobject.line.qrectf()
                elif isinstance(event.gobject, Point):
                    # point
                    self._point_moving_counter = 0
                    self._point_moving = event.gobject
                    self._point_moving_old = event.gobject.point.qpointf()

    def wheelEvent(self, event):
        """wheel event for zooming"""
        if cfg.diagram is None:
            return
        delta = event.delta()/3000
        if delta>0.1:
            delta = 0.1
        if delta<-0.1:
            delta = -0.1        
        # repair possition
        cfg.diagram.x +=  (event.scenePos().x() -  cfg.diagram.x) * delta
        cfg.diagram.y += (event.scenePos().y() - cfg.diagram.y) * delta
        # repair zoom
        cfg.diagram.zoom *= (1.0 + delta)
        # send signal
        self.possChanged.emit()
