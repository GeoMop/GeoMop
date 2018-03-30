from gm_base.polygons.polygons import PolygonDecomposition, PolygonChange
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import numpy as np


class PolygonOperation():
    """
    Class for polygon localization
    """
#    line_spliting = None
#    """Note about spliting line in next add operation"""
#    label = None
#    """History label for this operation"""
#    not_history = True
#    """Not save this operation to history"""

    def __init__(self, line=None):
        self.decomposition = PolygonDecomposition()
        res = self.decomposition.get_last_polygon_changes()
        assert res[0] == PolygonChange.add
        self.outer_id = res[1]
        """ Decomposition of the a plane into polygons."""
        self.tmp_line = None
        """Line that will be reuse after line splitting"""
        self.tmp_polygon_id = None
        self.rest_polygon_id = None
        """Polygon that will be  created during removing splitted line"""
        
    def set_new_decomposition(self, diagram, decomposition):
        """set new decomposition"""
        self.decomposition = decomposition
        for segment in self.decomposition.segments.values():
            diagram.join_line_import(segment.vtxs[0].id, segment.vtxs[1].id, segment)
        for polygon in self.decomposition.polygons.values():
            if polygon.id!=self.outer_id:
                self._add_polygon(diagram, polygon.id, None, True)

    def add_point(self, diagram, point):
        """Add new point to decomposition"""
        if self.rest_polygon_id is not None:
            polygon_id = self.rest_polygon_id
            self.rest_polygon_id = None
        else:
            polygon_id = self._find_in_polygon(diagram, point)
        self.decomposition.add_free_point(point.id, (point.x, -point.y), polygon_id)        

    def move_points(self, diagram, points):
        """move set point in decomposition, return if all moving is possible"""
        ret = True
        if len(points)<1:
            return True
        p0 =  self.decomposition.points[points[0].de_id]
        dx = points[0].x-p0.xy[0]
        dy = -points[0].y-p0.xy[1]
        displacement = np.array([dx, dy])
        spoints = []
        for point in points:
            spoints.append(self.decomposition.points[point.de_id])
        new_displ = self.decomposition.check_displacment(spoints, displacement, 0.01)
        if new_displ[0]!=displacement[0] or new_displ[1]!=displacement[1]:
            ret = False
            for point in points:
                point.x += new_displ[0]-displacement[0]
                point.y -= new_displ[1]-displacement[1]
        self.decomposition.move_points(spoints, new_displ)
        res = self.decomposition.get_last_polygon_changes()
        if res[0]==PolygonChange.shape:
            for polygon_id in res[1]:
                if polygon_id!=self.outer_id:
                    self._reload_boundary(diagram, polygon_id)
        elif res[0]!=PolygonChange.none:
            raise Exception("Invalid polygon change during move point.")
        return ret

    def remove_point(self, diagram, point):
        """remove set point from decomposition"""
        self.decomposition.remove_free_point(point.de_id)
        
    def add_line(self, diagram, line, label=None, not_history=True):
        """Add new point to decomposition"""
        if self.tmp_line is not None:
            segment = self.decomposition.new_segment(
                self.decomposition.points[self.tmp_line.p1.de_id], 
                self.decomposition.points[self.tmp_line.p2.de_id])
            self.tmp_line.segment = segment 
            res = self.decomposition.get_last_polygon_changes()
            if res[0]!=PolygonChange.shape and res[0]!=PolygonChange.none:
                raise Exception("Invalid polygon change during split line.")  
            self.tmp_line = None
        segment = self.decomposition.new_segment(
            self.decomposition.points[line.p1.de_id], 
            self.decomposition.points[line.p2.de_id])
        line.segment = segment 
        res = self.decomposition.get_last_polygon_changes()
        if res[0]==PolygonChange.shape:
            for polygon_id in res[1]:
                if polygon_id!=self.outer_id:
                    self._reload_boundary(diagram, polygon_id)
        elif res[0]==PolygonChange.add:
            if self.tmp_polygon_id is None:
                self._add_polygon(diagram, res[2], label, not_history)
                return True
            else:
                self._assign_add(diagram, res[2])                
        elif res[0]==PolygonChange.split:
            if self.tmp_polygon_id is None:
                self._split_polygon(diagram, res[2], res[1], label, not_history)                
                return True
            else:
                self._assign_split(diagram, res[2], res[1])                
        elif res[0]!=PolygonChange.none:
            raise Exception("Invalid polygon change during add line.")
        return False
    
    def split_line(self, diagram, line):
        """remove and move line"""
        self.tmp_line = line
        self.decomposition.delete_segment(line.segment)
        res = self.decomposition.get_last_polygon_changes()
        if res[0]==PolygonChange.shape:
            if len(res[1])!=1:
                raise Exception("Invalid count of changed polygons.")
            self.rest_polygon_id = res[1][0]
        elif res[0]==PolygonChange.remove:
           self.rest_polygon_id = res[1]
           self.tmp_polygon_id = res[2]
        elif res[0]==PolygonChange.join:
            self.rest_polygon_id = res[1]
            self.tmp_polygon_id = res[2]
        elif res[0]!=PolygonChange.none:
            raise Exception("Invalid polygon change during split line.")
        
    def remove_line(self, diagram, line, label=None, not_history=True):
        """remove set point from decomposition"""
        self.decomposition.delete_segment(line.segment)
        res = self.decomposition.get_last_polygon_changes()
        if res[0]==PolygonChange.shape:
            for polygon_id in res[1]:
                if polygon_id!=self.outer_id:
                    self._reload_boundary(diagram, polygon_id)
        elif res[0]==PolygonChange.remove:
            self._remove_polygon(diagram, res[2], res[1], label, not_history)
        elif res[0]==PolygonChange.join:
            self._join_polygon(diagram, res[1], res[2], label, not_history)
        elif res[0]!=PolygonChange.none:
            raise Exception("Invalid polygon change during remove line.")
            
    def get_polygon_origin_id(self, polygon):
        """Return polygon id in origin structure"""
        return self.decomposition.polygons[polygon.helpid].index
    
    def get_line_origin_id(self, line):
        """Return line id in origin structure"""
        return line.segment.index
        
    def get_point_origin_id(self, point_id):
        """Return point id in origin structure"""
        return self.decomposition.points[point_id].index
    
    def _find_in_polygon(self, diagram, point, polygon_id=None):
        """Find polygon for set point"""
        if polygon_id is None:
            polygon_id = self.outer_id
        childs = self.decomposition.get_childs(polygon_id)
        for id in childs:
            if id!=polygon_id:
                children = self.decomposition.polygons[id].qtpolygon
                if children.containsPoint(point.qpointf(), QtCore.Qt.OddEvenFill):
                    return self._find_in_polygon(diagram, point, id)
        return polygon_id        
    
    def _reload_boundary(self, diagram, polygon_id):
        """reload set polygon boundary"""
        spolygon = self._get_spolygon(diagram, polygon_id)
        polygon = self.decomposition.polygons[polygon_id]
        lines, qtpolygon = self._get_lines_and_qtpoly(diagram, polygon)
        for line in lines:
            if not line in spolygon.lines:
                line.add_polygon(spolygon)
                spolygon.lines.append(line)
        rem_lines = []
        for line in spolygon.lines:
            if not line in lines:
                rem_lines.append(line)
        for line in rem_lines:
            spolygon.lines.remove(line)
            line.del_polygon(spolygon)
        spolygon.qtpolygon = qtpolygon
        polygon.qtpolygon = qtpolygon
        spolygon.helpid = polygon_id
        spolygon.depth = polygon.depth()
        if spolygon.object is not None:
            spolygon.object.refresh_polygon()
        
    def _assign_add(self, diagram, added_id):
        """Assign added polzgon to existing polygon in diagram"""
        spolygon = self._get_spolygon(diagram, self.tmp_polygon_id)
        spolygon.helpid = added_id
        self._reload_boundary(diagram, added_id)
        self.tmp_polygon_id = None
        
    def _assign_split(self, diagram, added_id, old_id):
        """Assign added polygon to existing polygon in diagram"""
        spolygon = self._get_spolygon(diagram, self.tmp_polygon_id)
        spolygon.helpid = added_id
        self._reload_boundary(diagram, added_id)
        self._reload_boundary(diagram, old_id)
        self.tmp_polygon_id = None
      
    def _get_spolygon(self, diagram, polygon_id):  
        spolygon = None
        for spoly in diagram.polygons:
            if spoly.helpid==polygon_id:
                spolygon = spoly
                break
        return spolygon
        
    def _fix_lines(self, diagram, polygon_id, polygon_old_id):
        """delete reference to old polygon in polygon lines"""
        polygon = self.decomposition.polygons[polygon_id]
        old_spolygon = self._get_spolygon(diagram, polygon_old_id)
        points = polygon.vertices()
        for i in range(0, len(points)):            
            if i==0:
                line = diagram.find_line(points[-1].id, points[0].id)
            else:
                line = diagram.find_line(points[i-1].id, points[i].id)
            line.del_polygon(old_spolygon)        
        
    def _reload_depth(self, diagram, polygon_id):
        """reload polygon depth recursivly"""
        spolygon = self._get_spolygon(diagram, polygon_id)
        if spolygon is None:
            return
        polygon = self.decomposition.polygons[polygon_id]

        # Temorary fix.
        # TODO: Do not call _reload_depth
        if spolygon is None:
            return

        spolygon.depth = polygon.depth()
        if spolygon.object is not None:
            spolygon.object.update_depth()
        childs = self.decomposition.get_childs(polygon_id)
        for children in childs:
            spolygon = self._get_spolygon(diagram, children)
            polygon = self.decomposition.polygons[children]
            spolygon.depth = polygon.depth()
        
    def _get_lines_and_qtpoly(self, diagram, polygon):
        """Return lines and qt polygon"""
        points = polygon.vertices()
        qtpolygon = QtGui.QPolygonF()
        lines = []        
        for i in range(0, len(points)):            
            qtpolygon.append(QtCore.QPointF(points[i].xy[0], -points[i].xy[1]))
            if i==0:
                line = diagram.find_line(points[-1].id, points[0].id)
            else:
                line = diagram.find_line(points[i-1].id, points[i].id)
            if line is None:
                raise Exception("Can't find polygon line in diagram")
            lines.append(line)
        qtpolygon.append(QtCore.QPointF(points[0].xy[0], -points[0].xy[1]))
        return lines, qtpolygon
        
    def _add_polygon(self, diagram, polygon_id, label, not_history, copy_id=None):
        """Add polygon to boundary"""
        polygon = self.decomposition.polygons[polygon_id]
        if polygon == self.decomposition.outer_polygon:
            return
        childs = self.decomposition.get_childs(polygon_id)
        for children in childs:
            if children!=polygon_id:
                self._reload_depth(diagram, children)
        copy = None
        if copy_id is not None:
            copy = self._get_spolygon(diagram, copy_id)
        lines, qtpolygon = self._get_lines_and_qtpoly(diagram, polygon)
        spolygon = diagram.add_polygon(lines, label, not_history, copy)
        spolygon.qtpolygon = qtpolygon
        polygon.qtpolygon = qtpolygon
        spolygon.helpid = polygon_id
        spolygon.depth = polygon.depth()
        
    def _remove_polygon(self, diagram, polygon_id, parent_id, label, not_history):
        """Add polygon to boundary"""
        childs = self.decomposition.get_childs(parent_id)
        for children in childs:
            if children!=parent_id:
                self._reload_depth(diagram, children) 
        spolygon = self._get_spolygon(diagram, polygon_id)               
        diagram.del_polygon(spolygon, label, not_history)

    def _split_polygon(self, diagram, polygon_id, polygon_old_id, label, not_history):
        """split poligon"""
        self._reload_boundary(diagram, polygon_old_id)
        self._fix_lines(diagram, polygon_id, polygon_old_id)
        self._add_polygon(diagram, polygon_id, label, not_history, polygon_old_id)
        
    def _join_polygon(self, diagram, polygon_id, del_polygon_id, label, not_history):
        """Join to polygons"""
        spolygon = self._get_spolygon(diagram, polygon_id)
        del_spolygon = self._get_spolygon(diagram, del_polygon_id)
        regions = spolygon.cmp_polygon_regions(diagram, del_spolygon)
        diagram.del_polygon(del_spolygon, label, not_history)
        if regions is not None:
            spolygon.set_regions(diagram, regions, None, not_history)
            spolygon.object.update_color()
        self._reload_boundary(diagram, polygon_id)
        
    @classmethod
    def try_intersection(cls, diagram, p1, p2, label):
        """
        Try look up intersection and split lines. Return new points, and_lines.
        Points is sorted from p1 to p2.
        """
        new_points = []
        new_lines = []
        
        iline = QtCore.QLineF(p1.qpointf(), p2.qpointf())
        res_lines = []
        for line in diagram.lines:
            if line.p1==p1 or line.p1==p2 or line.p2==p1 or line.p2==p2:
                continue
            new_point = QtCore.QPointF()
            if iline.intersect(line.qlinef(), new_point) == QtCore.QLineF.BoundedIntersection:                
                new_points.append(new_point)
                res_lines.append(line)
                
        for i in range(0, len(res_lines)):   
            if label == "Add line":
                label = "Add intersected line"
            p, l = diagram.add_new_point_to_line(res_lines[i], new_points[i].x(), 
                new_points[i].y(), label)
            label = None
            new_lines.append(l)
            new_points[i] = p
            
        if len(new_points)>1:
            if p1.x<p2.x:
                new_points.sort(key=lambda p: p.x)
            else:
                new_points.sort(key=lambda p: p.x, reverse=True)               
        
        return new_points, new_lines, label
