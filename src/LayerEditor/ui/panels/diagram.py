"""Diagram file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import numpy as np
from ..data import diagram_structures as struc
from ..data.selection import Selection
from ..gitems import Line, Point, ShpBackground, DiagramView, Blink, Polygon, InitArea, Grid
from ..gitems import ItemStates
from LayerEditor.leconfig import cfg
    
class Diagram(QtWidgets.QGraphicsScene):
    """
    GeoMop Layer Editor design area
    
    Y coordinetes is negative for right map orientation. For displaying or setting
    is need set opposite value.
    
    pyqtSignals:
        * :py:attr:`cursorChanged(float, float) <cursorChanged>`
        * :py:attr:`possChanged() <possChanged>`
        * :py:attr:`regionsUpdateRequired() <regionUpdateRequired>`
        * :py:attr:`setArea() <setArea>`
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
    regionsUpdateRequired = QtCore.pyqtSignal()
    """
    Shape was clicked and all regions in current topology update 
    in region panel is required
    """
    BLINK_INTERVAL = 500
    """blink interval in ms"""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """ 
        # add point
        self._add_new_point = False
        self._add_new_point_counter = 0
        """counter for add point"""
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
        self._line_moving_old_pos = None
        """Old line grab position"""
        # move canvas variables
        self._moving = False
        """scene is drawn"""
        self._moving_x = 0
        """last x-coordinates for moving"""
        self._moving_y = 0
        """last y-coordinates for moving"""
        self._moving_counter = 0
        """counter for moving"""
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
        self.selection = Selection()
        """selection operations"""
        # control object
        self._control_object = None
        """object, that is below cursor, if button press event is emited"""
        #blink
        self.blink = None
        """blink object"""
        self.blink_timer = QtCore.QTimer()
        """Blink timer"""
        self.init_area=None
        """Initialization area"""
        self.blink_timer.setSingleShot(True) 
        #mash
        self.grid=None
        """Surface mash"""        
        
        super(Diagram, self).__init__(parent)
        self.blink_timer.timeout.connect(self.blink_end)
        self.blink_timer.start(self.BLINK_INTERVAL) 
  
        self.set_data()    
        self.setSceneRect(0, 0, 20, 20)

    def remove_graphical_object(self, obj):
        """Remove the object from the graphics scene and emit appropriate update signals"""
        # remove the object from the graphical scene
        self.removeItem(obj)
        # update the regions panel in case some region is no longer in use and can be deleted
        self.regionsUpdateRequired.emit()

    def add_graphical_object(self, obj):
        """Add the object to the graphics scene and emit appropriate update signals"""
        # Add the object from the graphics scene
        self.addItem(obj)
        #update the regions panel in case some region gets in use and therefore cannot be deleted.
        self.regionsUpdateRequired.emit()
        # # Get object dimension, selected layer,..
        # dim = None
        # layer_id = cfg.diagram.regions.current_layer_id
        # if isinstance(obj, Point):
        #     dim = 0
        # elif isinstance(obj, Line):
        #     dim = 1
        # elif isinstance(obj, Polygon):
        #     dim = 2
        # if dim is not None:
        #     #..selected region in the regions panel
        #     reg_id = cfg.main_window.regions.get_current_region()
        #     if not reg_id == 0:
        #         # ..and compare the dimensions with all aspects (region dimension, fracture/bulk layer,..)
        #         region = cfg.diagram.regions.regions[reg_id]
        #         pas = region.cmp_shape_dim(layer_id, dim)
        #         # if the region is actually added to the new object, update the region panel
        #         if pas:
        #             self.regionsUpdateRequired.emit()

    def show_grid(self, quad, nuv):
        """Show grid of actual surface from surface panel."""
        if quad is None:
            return
        if self.grid is None:
            self.grid = Grid(quad, nuv)
            self.add_graphical_object(self.grid)
        else:
            self.grid.set_quad(quad, nuv)
        return self.grid.boundingRect()
        
    def hide_grid(self):
        """hide mash"""
        if self.grid is not None:
            self.remove_graphical_object(self.grid)
            self.grid = None
        
    def  show_init_area(self, state):
        """Show initialization area"""
        if self.init_area is not None:
            self.remove_graphical_object(self.init_area)
        if state:
            self.init_area = InitArea(cfg.diagram)
            self.add_graphical_object(self.init_area)
        
    def refresh_shp_backgrounds(self):
        """refresh updated shape files on background"""
        for shp in cfg.diagram.shp.datas:
            if shp.shpdata.object is None:
                s = ShpBackground(shp.shpdata, shp.color)
                self.add_graphical_object(s)
               # s.prepareGeometryChange()
                shp.refreshed = True
            elif not shp.refreshed:
                shp.shpdata.object.color = shp.color
                shp.shpdata.object.update()
                shp.refreshed = True
    
    def _add_point(self, gobject, p1, label='Add point', add_next=False):
        """Add point to diagram and paint it."""
        if gobject is None or isinstance(gobject, Polygon):
            point =cfg.diagram.add_point(p1.x(), p1.y(), label) 
            p = Point(point)
            self.add_graphical_object(p)
        elif isinstance(gobject, Point):
            return gobject, label
        elif isinstance(gobject, Line): 
            if label=='Add point':
                label='Add new point to line'
            point, l2 = cfg.diagram.add_new_point_to_line(gobject.line_data, p1.x(), p1.y(), label)
            l = Line(l2)
            self.add_graphical_object(l)
            p = Point(point)
            self.add_graphical_object(p)
            self._add_polygons()
        if add_next:
            self._last_p1_real = p
            self._last_p1_on_line = None
            self._remove_last()
            line = struc.Diagram.make_tmp_line(p1.x(), p1.y(), p1.x(), p1.y())
            pt1 = Point(line.p1, tmp=True)
            self.add_graphical_object(pt1)
            pt2 = Point(line.p2, tmp=True)
            pt2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.add_graphical_object(pt2)
            l = Line(line, tmp=True)
            self.add_graphical_object(l)
            self._last_line = line
            self._add_polygons()
        return p, None
        
    def _add_polygons(self):
        """If is new polygon in data object, create it"""
        if len(cfg.diagram.new_polygons)>0:
            for polygon in cfg.diagram.new_polygons:
                obj = polygon.object
                if obj is not None:
                    obj.release_polygon()
                    self.remove_graphical_object(obj)
                p = Polygon(polygon)
                self.add_graphical_object(p)
            cfg.diagram.new_polygons = []
            
    def _del_polygons(self):
        """If is deleted polygon in data object, delete it"""
        if len(cfg.diagram.deleted_polygons)>0:
            for polygon in cfg.diagram.deleted_polygons:
                obj = polygon.object
                if obj is not None:                    
                    obj.release_polygon()
                    self.remove_graphical_object(obj)
                if polygon in self.selection.selected_polygons:
                    self.selection.selected_polygons.remove(polygon)
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
                px = gobject.point_data.x
                py = gobject.point_data.y
            elif isinstance(gobject, Line):
                self._last_p1_real = None
                self._last_p1_on_line = gobject
                px, py =  struc.Diagram.get_point_on_line(gobject.line_data, p.x(), p.y())
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
            px = p2.point_data.x
            py = p2.point_data.y
            # px = p.x()
            # py = p.y()
            added_points, moved_points, added_lines = cfg.diagram.join_line_intersection(
                p1.point_data, p2.point_data, label)
            self.update_changes(added_points, [], moved_points, added_lines, [])
            self._last_p1_real = p2
            self._last_p1_on_line = None
            self._remove_last()
            self._add_polygons()
            self._del_polygons()
        if add_last:
            line = struc.Diagram.make_tmp_line(px, py, p.x(), p.y())
            p1 = Point(line.p1, tmp=True)
            self.add_graphical_object(p1)
            p2 = Point(line.p2, tmp=True)
            p2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.add_graphical_object(p2)            
            l = Line(line, tmp=True)
            self.add_graphical_object(l)
            self._last_line = line
            self._add_polygons()
        
    def _remove_last(self):
        """Remove last point and line from diagram."""
        if self._last_line is not None:
            p1 = self._last_line.p1.object
            p2 = self._last_line.p2.object
            l = self._last_line.object
            p1.release_point()
            self.remove_graphical_object(p1)
            p2.release_point()
            self.remove_graphical_object(p2)
            self._last_line.object.release_line()
            self.remove_graphical_object(l)
            self._last_line = None            
    
    def update_changes(self, added_points, removed_points, moved_points, added_lines, removed_lines):
        for point in added_points:
            p = Point(point)
            self.add_graphical_object(p)
        for line in added_lines:
            l = Line(line)
            self.add_graphical_object(l)
        for point in removed_points:
            p = point.object
            p.release_point()
            self.remove_graphical_object(p)
        for line in removed_lines:
            l = line.object
            l.release_line()
            self.remove_graphical_object(l)
        for point in moved_points:
            point.object.move_point()
        
    def release_views(self):
        """release all diagram views"""
        deleted = []
        for uid, view in cfg.diagram.views_object.items():
            deleted.append(view)
        cfg.diagram.views_object = {}
        while len(deleted)>0:
            self.remove_graphical_object(deleted.pop())
        
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
            self.remove_graphical_object(obj)
        for uid in cfg.diagram.views:
            if curr_uid!=uid and uid not in cfg.diagram.views_object:    
                view = DiagramView(uid)
                self.add_graphical_object(view)
        
    def release_data(self, old_diagram):
        """release all shapes data"""
        for line in cfg.diagrams[old_diagram].lines:
            obj = line.object
            obj.release_line()
            self.remove_graphical_object(obj)
        for point in cfg.diagrams[old_diagram].points:
            obj = point.object
            obj.release_point()
            self.remove_graphical_object(obj)
        for polygon in cfg.diagrams[old_diagram].polygons:
            obj = polygon.object
            obj.release_polygon()
            self.remove_graphical_object(obj)
        
    def set_data(self):        
        """set new shapes data"""
        for line in cfg.diagram.lines:
            l = Line(line)
            self.add_graphical_object(l)
        for point in cfg.diagram.points:
            p = Point(point)
            self.add_graphical_object(p)
            for polygon in cfg.diagram.polygons:
                if polygon.object is None:
                    p = Polygon(polygon)
                    self.add_graphical_object(p)
        self._add_polygons()
        
    def blink_start(self, rect):
        """Start blink window"""
        self.blink = Blink(rect)
        self.add_graphical_object(self.blink)
        self.blink_timer.start(self.BLINK_INTERVAL)
        
    def blink_end(self):
        """Finish blink window"""
        if self.blink is not None:
            self.remove_graphical_object(self.blink)
        self.blink = None
            
    def update_geometry(self):
        """Update geometry of shapes according to actual zoom"""
        for line in cfg.diagram.lines:
            line.object.update_geometry()
        for point in cfg.diagram.points:
            point.object.update_geometry()
        for polygon in cfg.diagram.polygons:
            polygon.object.update_geometry()

    def mouseMoveEvent(self, event):
        """Standart mouse event"""
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)
        if self._add_new_point:
            self._add_new_point_counter += 1
        if self._moving:    # Moving the diagram view by RMB drag
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
                # displacement from old position
                displacement = event.scenePos() - self._point_moving_old
                # point at old position
                point_data = cfg.diagram.po.decomposition.points[self._point_moving.point_data.de_id]
                if cfg.diagram.po.decomposition.check_displacment(
                        [point_data], np.array([displacement.x(), -displacement.y()])):
                    if self._point_moving_counter == 3:
                        self._point_moving.move_point(event.scenePos(), ItemStates.moved)
                    else:
                        self._point_moving.move_point(event.scenePos())
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        elif self._line_moving is not None:
            self._line_moving_counter += 1
            if self._line_moving_counter%3==0:
                # point at old position
                displacement = event.scenePos() - self._line_moving_old_pos
                p1_data = cfg.diagram.po.decomposition.points[self._line_moving.line_data.p1.de_id]
                p2_data = cfg.diagram.po.decomposition.points[self._line_moving.line_data.p2.de_id]
                if cfg.diagram.po.decomposition.check_displacment(
                        [p1_data, p2_data], np.array([displacement.x(), -displacement.y()])):
                    if self._line_moving_counter == 3:
                        self._line_moving.shift_line(event.scenePos()-self._line_moving_pos, ItemStates.moved)
                    else:
                        self._line_moving.shift_line(event.scenePos()-self._line_moving_pos)
                    self._line_moving_pos = event.scenePos()
            else:
                self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())
        else:
            self.cursorChanged.emit(event.scenePos().x(), event.scenePos().y())

    def select_all(self):
        """select all items"""
        self.selection.select_all()
        self.regionsUpdateRequired.emit()

    def delete_selected(self):
        """delete selected"""
        objects_to_remove = self.selection.delete_selected()
        if len(objects_to_remove) > 0:
            for obj in objects_to_remove:
                self.remove_graphical_object(obj)
            self._del_polygons()
        else:
            self.regionsUpdateRequired.emit()

    def _anchor_moved_point(self, event):
        """Test if point collide with other and move it"""
        below_items = self.items(event.scenePos())
        not_obstructed = any([item == self._point_moving for item in below_items]) #if the moving is not in the stack, its hindered somewhere
        below_item = below_items[0]  # topmost
        if below_item == self._point_moving:
            # moved point with small zorder value is below cursor (normal case, no obstructions - small z point is the temporary one)
            self._point_moving.move_point(event.scenePos(), ItemStates.standart)
            if not cfg.diagram.update_moving_points([self._point_moving.point_data]):
                self._point_moving.move_point(QtCore.QPointF(
                    self._point_moving.point_data.x, self._point_moving.point_data.y))
            cfg.diagram.move_point_after(self._point_moving.point_data,
                self._point_moving_old.x(), self._point_moving_old.y())
        elif isinstance(below_item, Line) and len(self._point_moving.point_data.lines) == 1 and not_obstructed:
            cfg.diagram.move_point_after(self._point_moving.point_data,self._point_moving_old.x(),
                self._point_moving_old.y(), 'Move point to Line')
            new_line, merged_lines = cfg.diagram.add_point_to_line(below_item.line_data,
                self._point_moving.point_data, None)
            l = Line(new_line)
            self.add_graphical_object(l)
            self._point_moving.move_point(QtCore.QPointF(
                self._point_moving.point_data.x, self._point_moving.point_data.y), ItemStates.standart)
            self.update_changes([], [],  [], [], merged_lines)
        elif isinstance(below_item, Point) and len(self._point_moving.point_data.lines) == 1 and not_obstructed:
            cfg.diagram.move_point_after(self._point_moving.point_data,self._point_moving_old.x(),
                self._point_moving_old.y(), 'Merge points')
            removed_lines = cfg.diagram.merge_point(below_item.point_data, self._point_moving.point_data, None)
            self._point_moving.release_point()
            self.remove_graphical_object(self._point_moving)
            self.update_changes([], [],  [], [], removed_lines)            
            below_item.move_point(event.scenePos(), ItemStates.standart)
        else:
            # Path obstructed
            self._point_moving.move_point(QtCore.QPointF(
                self._point_moving.point_data.x, self._point_moving.point_data.y), ItemStates.standart)
            if not cfg.diagram.update_moving_points([self._point_moving.point_data]):
                self._point_moving.move_point(QtCore.QPointF(
                    self._point_moving.point_data.x, self._point_moving.point_data.y))
            cfg.diagram.move_point_after(self._point_moving.point_data,
                self._point_moving_old.x(), self._point_moving_old.y())
        self._add_polygons()
        self._del_polygons()        
            
    def mouseReleaseEvent(self,event):
        event.gobject = None
        super(Diagram, self).mouseMoveEvent(event)
        end_moving = False
        below_items = self.items(event.scenePos())
        if self._add_new_point:
            self._add_new_point = False
            if self._add_new_point_counter > 5:
                return
        if self._moving:
            self._moving = False
            if self._moving_counter > 1:
                cfg.diagram.x += (self._moving_x-event.screenPos().x())/cfg.diagram.zoom
                cfg.diagram.y += (self._moving_y-event.screenPos().y())/cfg.diagram.zoom
                self.possChanged.emit()
                end_moving = True

        if event.button() == QtCore.Qt.LeftButton and \
                event.modifiers() == QtCore.Qt.NoModifier:
            if self._point_moving is not None:
                # either moving point or clicked on existing one
                if self._point_moving_counter > 1:
                    # TODO: take care of cases when point is moving in wrong manner, e.g. creating overlapping lines. This should be taken care of on data layer.
                    # if the point is actually moving in space (mouseMoveEvent occurred)
                    self._anchor_moved_point(event)
                else:
                    # this is a workaround for mousePressEvent setting up the _point_moving
                    if self._last_p1_real is not None and list(set(self._last_p1_real.point_data.lines) & set(self._point_moving.point_data.lines)):
                        # if any of the start point lines are identical with the end point lines,
                        #  two overlapping lines would be created -> don't create anything
                        self._remove_last()
                        self._last_p1_real = None
                        self._last_p1_on_line = None
                        self._last_line = None
                        # and start creating from the new point
                        self._add_line(event.gobject, event.scenePos())
                    else:
                        # In case of beginning the creation - create setup last_p1_real and create tmp elements
                        #  or in case of connecting to an existing real point
                        self._add_line(event.gobject, event.scenePos())
                # anchored or entered 'creation' mode with tmp elements through else statement above,
                #   no point is moving anymore
                self._point_moving = None
            elif self._line_moving is not None:
                # TODO: take care of cases when line is moving and its points should create duplicate lines (return back over another line). This should be taken care of on data layer.
                if self._line_moving_counter>1:
                    self._line_moving.shift_line(event.scenePos()-self._line_moving_pos, ItemStates.standart)
                    if not cfg.diagram.update_moving_points([self._line_moving.line_data.p1, self._line_moving.line_data.p2]):
                        self._line_moving.line_data.p1.object.move_point(QtCore.QPointF(
                            self._line_moving.line_data.p1.x, self._line_moving.line_data.p1.y))
                        self._line_moving.line_data.p2.object.move_point(QtCore.QPointF(
                            self._line_moving.line_data.p2.x, self._line_moving.line_data.p2.y))
                    cfg.diagram.move_point_after(self._line_moving.line_data.p1,
                       self._line_moving_old[0].x(), self._line_moving_old[0].y(), "Move line")        
                    cfg.diagram.move_point_after(self._line_moving.line_data.p2,
                       self._line_moving_old[1].x(), self._line_moving_old[1].y(), None)                            
                else:
                    self._add_line(event.gobject, event.scenePos())
                self._line_moving = None
            else:
                # creation of elements
                if self._last_line is not None:
                    # case line is created as well, i.e. second click.
                    if self._last_line.p1 in [point.point_data for point in below_items if isinstance(point, Point)]:
                        # eliminate the case when starting point of the line corresponds to the end point,
                        # i.e. zero length line creation case -> double click on the same position creates real point
                        self._add_point(event.gobject, event.scenePos(), add_next=True)
                    else:
                        # normal addition of line
                        self._add_line(event.gobject, event.scenePos())
                else:
                    # First point - all set up in add_line method, including temporary line and end point
                    self._add_line(event.gobject, event.scenePos())
        if event.button()==QtCore.Qt.LeftButton and \
            event.modifiers()==QtCore.Qt.ControlModifier:
            if self._point_moving is not None:
                if self._point_moving_counter > 1:
                    # in case ctrl was pressed on release when point is actually moving (mouseMoveEvent occurred), this should mirror the no modifier
                    self._anchor_moved_point(event)
                    self._point_moving = None
            elif self._last_line is not None:
                # case line is created as well, i.e. second click.
                points_underneath = [point.point_data for point in below_items if
                                     isinstance(point, Point) and point.point_data is not self._last_line.p2]
                if self._last_line.p1 in points_underneath:
                    # eliminate the case when starting point of the line corresponds to the end point,
                    # i.e. zero length line creation case
                    if self._last_p1_real is not None:
                        # if the first point already exists dont create new one
                        pass
                    else:
                        # the first point is tmp as well -> create it
                        self._add_point(event.gobject, event.scenePos())
                    # delete the tmp elements and reset appropriate variables
                    self._remove_last()
                    self._last_p1_real = None
                    self._last_p1_on_line = None
                    self._last_line = None
                elif (self._last_p1_real is not None) and points_underneath \
                        and list(set(self._last_p1_real.point_data.lines) & set(points_underneath[0].lines)):
                    # if any of the start point lines are identical with the end point lines,
                    #  two overlaping lines would be created -> dont create anything
                    self._remove_last()
                    self._last_p1_real = None
                    self._last_p1_on_line = None
                    self._last_line = None
                else:
                    # simple creation in normal cases terminating the tmp elements (third 'False' parameter)
                    self._add_line(event.gobject, event.scenePos(), False)
            else:
                # creation of point only
                self._add_point(event.gobject, event.scenePos())
                
        if event.button()==QtCore.Qt.RightButton:
            if event.modifiers()==QtCore.Qt.NoModifier and not end_moving:
                self.selection.deselect_selected()
                if event.gobject is not None:
                    if isinstance(event.gobject, Line):
                        self.selection.select_line(event.gobject.line_data, True)
                    elif isinstance(event.gobject, Point):
                        self.selection.select_point(event.gobject.point_data)
                    elif isinstance(event.gobject, Polygon):
                        self.selection.select_polygon(event.gobject.polygon_data)
                    self.regionsUpdateRequired.emit()
            if event.modifiers()==QtCore.Qt.ShiftModifier:
                if event.gobject is not None:
                    if isinstance(event.gobject, Line):
                        self.selection.select_line(event.gobject.line_data, True)
                    elif isinstance(event.gobject, Point):
                        self.selection.select_point(event.gobject.point_data)
                    elif isinstance(event.gobject, Polygon):
                        self.selection.select_polygon(event.gobject.polygon_data)
                    if not self.selection.is_empty():
                        self.regionsUpdateRequired.emit()
            if event.modifiers()==QtCore.Qt.ControlModifier:
                if self.selection.is_empty():
                    self.selection.select_current_region()
            if event.modifiers()==QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier:
                if event.gobject is not None:
                    if isinstance(event.gobject, Polygon):
                        event.gobject.polygon_data.set_current_regions()
                        event.gobject.update_color()
                    elif isinstance(event.gobject, Line):
                        event.gobject.line_data.set_current_regions()
                        event.gobject.update_color()
                    elif isinstance(event.gobject, Point):
                        event.gobject.point_data.set_current_regions()
                        event.gobject.update_color()
            
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
        if event.button()==QtCore.Qt.RightButton and \
            event.modifiers()==QtCore.Qt.NoModifier:
            self._moving_counter = 0
            self._moving = True
            self._moving_x = event.screenPos().x()
            self._moving_y = event.screenPos().y()                
        if event.button()==QtCore.Qt.LeftButton:
            self.selection.deselect_selected()
            if event.modifiers()==QtCore.Qt.NoModifier:
                if event.gobject is not None:
                    if isinstance(event.gobject, Line):
                        self._line_moving_counter = 0
                        self._line_moving = event.gobject
                        self._line_moving_pos = event.scenePos()
                        self._line_moving_old_pos = event.scenePos()
                        self._line_moving_old = (event.gobject.line_data.p1.qpointf(), event.gobject.line_data.p2.qpointf())
                    elif isinstance(event.gobject, Point):
                        # point
                        self._point_moving_counter = 0
                        self._point_moving = event.gobject
                        self._point_moving_old = event.gobject.point_data.qpointf()
                    else:
                        self._add_new_point_counter = 0
                        self._add_new_point = True

                else:
                    self._add_new_point_counter = 0
                    self._add_new_point = True

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
        if cfg.diagram.pen_changed:
            self.update_geometry()
        # send signal
        self.possChanged.emit()
        
    def keyPressEvent(self, event):
        """Standart key press event"""
        if event.key() == QtCore.Qt.Key_Escape:
            self._remove_last()
        # elif event.key() == QtCore.Qt.Key_Delete:
        #     self.delete_selected()
        
    def focusInEvent(self, event):
        """Standart focus event"""
        super(Diagram, self).focusInEvent(event)
        # if self.grid is not None:
        #     self.hide_grid()

