import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from .shp_structures import ShpFiles
from .history import DiagramHistory
from .region_structures import Regions
from .polygon_operation import PolygonOperation

__next_id__ = 1
__next_diagram_uid__ = 1


class Point():
    """
    Class for graphic presentation of point
    """
    def __init__(self, x, y, id=None):
        global __next_id__
        self.x = x 
        """x coordinate"""
        self.y = y 
        """y coordinate"""
        self.lines = []
        """This point instance is use for these lines"""
        self.object = None
        """Graphic object""" 
        self.id = id
        """Point history id"""
        
        if id is None:            
            self.id = __next_id__
            __next_id__ += 1
            
    def qpointf(self):
        """return QPointF coordinates"""
        return QtCore.QPointF(self.x, self.y)
        
    def __lt__(self, other):
        """operators for comparation"""
        if self.x<other.x or (self.x==other.x and self.y<other.y):
            return True
        return False
        
    def __le__(self, other):
        """operators for comparation"""        
        if self.x<other.x:
            return True
        if self.x==other.x and self.y==other.y:
            assert self is other
            return True
        return False
        
    def __eq__(self, other):
        """operators for comparation"""
        return self is other
        
    def __ne__(self, other):
        """operators for comparation"""
        return self is not other
        
    def __gt__(self, other):
        """operators for comparation"""
        if self.x>other.x or (self.x==other.x and self.y>other.y):
            return True
        return False
        
    def __ge__(self, other):
        """operators for comparation"""
        if self.x>other.x:
            return True
        if self.x==other.x and self.y==other.y:
            assert self is other
            return True
        return False       
       
    def get_color(self):
        """Return line color"""
        return Diagram.regions.get_region_color(0, self.id)

    def set_current_region(self):
        """Set point region to current region"""
        Diagram.regions.set_region(0, self.id, True, "Set Region")
        
    def get_point_region(self):
        """Return polygon regions"""
        return Diagram.regions.get_region(0, self.id)
        
    def set_current_regions(self):
        """Set point region to current region"""
        Diagram.regions.set_regions(0, self.id, True, "Set Regions")
        
    def get_point_regions(self):
        """Return polygon regions"""
        return Diagram.regions.get_regions(0, self.id)


class Line():
    """
    Class for graphic presentation of line
    """
    def __init__(self, p1, p2, id=None):
        global __next_id__
        self.p1 = p1
        """First point"""
        self.p2 = p2
        """Second point"""
        self.object = None
        """Graphic object"""
        self.id = id
        """Line history id"""
        self.polygon1 = None
        """This line instance is use for these polygon"""
        self.polygon2 = None
        """This line instance is use for these polygon"""
        self.segment = None
        """This line instance is in these polygon"""
 
        if id is None:            
            self.id = __next_id__
            __next_id__ += 1

    def add_polygon(self, polygon):
        """Add polygon, that is use this line"""
        if self.polygon1 is None:
            self.polygon1 = polygon
        else:
            if self.polygon1 != polygon:
                if self.polygon2 is None:
                    self.polygon2 = polygon
                else:
                    raise Exception("Line can't be part more than one polygon.")
                    
    def del_polygon(self, polygon):
        """Add polygon, that is use this line"""
        if self.polygon1 == polygon:
            if self.polygon2 is None:
                self.polygon1 = None
            else:
                self.polygon1 = self.polygon2
                self.polygon2 = None
        elif self.polygon2 == polygon:
            self.polygon2 = None
                    
    def second_point(self, p):
        """return second line point"""
        if p==self.p1:
            return self.p2
        return self.p1
                    
    def count_polygons(self):
        """Delete polygon, that was use this line"""
        if self.polygon1 is None:
            return 0
        if self.polygon2 is None:
            return 1
        return 2

    def qrectf(self):
        """return QRectF coordinates"""
        return QtCore.QRectF(self.p1.qpointf(), self.p2.qpointf())
        
    def qlinef(self):
        """return QLineF object"""
        return QtCore.QLineF(self.p1.qpointf(), self.p2.qpointf())
        
    def get_tmp_line(self, p1, p2):
        return Line(p1, p2, -1)
        
    def get_color(self):
        """Return line color"""
        return Diagram.regions.get_region_color(1, self.id)
        
    def set_current_region(self):
        """Set polygon region to current region"""
        Diagram.regions.set_region(1, self.id, True, "Set Region")
        
    def get_line_region(self):
        """Return polygon regions"""
        return Diagram.regions.get_region(1, self.id)
        
    def set_current_regions(self):
        """Set polygon region to current region"""
        Diagram.regions.set_regions(1, self.id, True, "Set Regions")
        
    def get_line_regions(self):
        """Return polygon regions"""
        return Diagram.regions.get_regions(1, self.id)


class Polygon():
    """
    Class for graphic presentation of line
    """
    def __init__(self, lines, id=None):
        global __next_id__
        self.lines = []
        """Lines"""
        for line in lines:
            self.lines.append(line)
            if line.polygon1 is None:
                line.polygon1 = self
            else:
                line.polygon2 = self
            line.in_polygon = None
        self.object = None
        """Graphic object"""
        self.helpid = None
        """Id in polygon from decomposition"""
        self.id = id
        """Polygon history id"""
        self.qtpolygon = None
        """Qt polygon for point localization"""
        if id is None:            
            self.id = __next_id__
            __next_id__ += 1
        
    def get_color(self):
        """Return region color"""
        return Diagram.regions.get_region_color(2, self.id)

    def set_current_region(self):
        """Set polygon region to current region"""
        Diagram.regions.set_region(2, self.id, True, "Set Region")
        
    def set_current_regions(self):
        """Set polygon region to current region"""
        Diagram.regions.set_regions(2, self.id, True, "Set Regions")
        
    def get_polygon_regions(self):
        """Return polygon regions"""
        return Diagram.regions.get_regions(2, self.id)
        
    def get_polygon_region(self):
        """Return polygon regions"""
        return Diagram.regions.get_region(2, self.id)
 
class Area():
    """Initialization area"""
    
    def __init__(self):
        self.gtpolygon = None
        """displaing polygon"""
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        """boundary rect"""
        
    def serialize(self, points):
        """Return inicialization arrea in polygon coordinates"""
        for i in range(0, len(self.gtpolygon)-1):
            points.append((self.gtpolygon[i].x(),-self.gtpolygon[i].y()))
        
    def deserialize(self, points):
        """Set inicialization arrea from polygon coordinates"""
        px, py = zip(*points)
        self.set_area(px, py)
        
    def set_area(self, pxs, pys):
        """Set initialization area"""
        self.gtpolygon = QtGui.QPolygonF()        
        self.xmin = pxs[0]
        self.xmax = pxs[0]
        self.ymin = -pys[0]
        self.ymax = -pys[0]
        for x, y in zip(pxs, pxs):
            self.gtpolygon.append(QtCore.QPointF(x, -y))
            self.xmin = min(self.xmin, x)
            self.xmax = max(self.xmax, x)
            self.ymin = min(self.ymin, -y)
            self.ymax = max(self.ymax, -y)
        self.gtpolygon.append(QtCore.QPointF(pxs[0], -pys[0]))
 
class Diagram():
    """
    Layer diagram
    
    Use only class functions for adding new shapes. This function ensure folloving 
    requirements. New class function must ensure this requirements too.
    requirements:
        - All points is unique
        - All points contains used lines
        - Point is griater if is right or x coordinate is equol and point is below 
        - Line.p1<line.p2
    """
    shp = ShpFiles()
    """Displayed shape files"""
    views = []    
    """Not edited diagrams"""
    map_id = {}
    """uid, id map"""
    views_object = {}
    """Object of not edited diagrams"""
    topologies = {}
    """List of all diagrams, divided by topologies"""
    regions = None
    """List of regions"""
    area = Area()
    """diagram area"""
    
    @classmethod
    def add_region(cls, color, name, dim, step=0.01, boundary=False, not_used=False):
        """Add region"""
        cls.regions.add_region(color, name, dim, step, boundary, not_used)    
        
    @classmethod
    def add_shapes_to_region(cls, is_fracture, layer_id, layer_name, topology_idx, regions):
        """Add shape to region"""
        mapped_regions = [{}, {}, {}]
        diagram = cls.topologies[topology_idx][0]
        for point_id in range(0, len(diagram.points)):
            mapped_regions[0][diagram.points[point_id].id] = regions[0][diagram.po.get_point_origin_id(point_id)]
        for line in diagram.lines:
            mapped_regions[1][line.id] = regions[1][diagram.po.get_line_origin_id(line)]
        for polygon in diagram.polygons:
            mapped_regions[2][polygon.id] = regions[2][diagram.po.get_polygon_origin_id(polygon)]    
        cls.regions.add_shapes_to_region(
            is_fracture, layer_id, layer_name, topology_idx, mapped_regions)

    @classmethod
    def get_shapes_from_region(cls, is_fracture, layer_id):
        """Get shapes from region""" 
        regions = cls.regions.get_shapes_from_region(is_fracture, layer_id)        
        remapped_regions = [[], [], []]
        diagram = cls.topologies[cls.regions.find_top_id(layer_id)][0]
        tmp = {}
        for point_id in range(0, len(diagram.points)):
            tmp[diagram.po.get_point_origin_id(point_id)]=regions[0][diagram.points[point_id].id]
        remapped_regions[0] = [value for (key, value) in sorted(tmp.items())]  
        tmp = {}
        for line in diagram.lines:
            tmp[diagram.po.get_line_origin_id(line)]=regions[1][line.id]
        remapped_regions[1] = [value for (key, value) in sorted(tmp.items())]    
        for polygon in diagram.polygons:
            tmp[diagram.po.get_polygon_origin_id(polygon)]=regions[2][polygon.id]
        remapped_regions[2] = [value for (key, value) in sorted(tmp.items())]    
        
        return remapped_regions
                
    def region_color_changed(self, region_idx):
        """Region collor was changed"""
        for polygon in self.polygons:
            if self.regions.get_region_id(2, polygon.id)==region_idx:
                polygon.object.update_color()
# TODO: Lines and points
#            for i in range(0, len(diagram.lines)):                
#                map[top_id][1][i] = diagram.lines[i].id
#           for i in range(0, len(diagram.points)):
#                map[top_id][0][i] = diagram.points[i].id

    def layer_region_changed(self):
        """Layer color is changed, refresh all region collors"""
        for polygon in self.polygons:
            if polygon.object is not None:
                polygon.object.update_color()
            
# TODO: Lines and points
#            for i in range(0, len(diagram.lines)):                
#                map[top_id][1][i] = diagram.lines[i].id
#           for i in range(0, len(diagram.points)):
#                map[top_id][0][i] = diagram.points[i].id
                
    def get_polygon_lines(self, id):
        """Return polygon lines ndexes"""
        for polygon in self.polygons:
            if polygon.id==id:
                idxs = []
                for line in polygon.lines:
                    idxs.append(line.id)
                return idxs

    def update_moving_points(self, points):
        """Update moving point for polygon operations"""
        return self.po.move_points(self, points)        

    def find_polygon(self, line_idxs):
        """Try find poligon accoding to lines indexes"""
        for polygon in self.polygons:
            if len(line_idxs)==len(polygon.lines):
                ok = True
                for line in polygon.lines:
                    if not line.id in line_idxs:
                        ok = False
                        break
                if ok:                    
                    return polygon.id
    
    @classmethod
    def release_all(cls, history):
        """Discard all links"""
        cls.views = []    
        cls.views_object = {}
        cls.topologies = {}
        cls.regions = Regions(history)
        
    @classmethod
    def move_diagram_topologies(cls, id, diagrams):
        """Increase topology index from id,
        and fix topologies dictionary"""
        if not id < len(diagrams):
            # not fix after last diagram
            assert id == len(diagrams)
            return
        max_top = diagrams[-1].topology_idx+1
        if max_top in cls.topologies:
            raise Exception("Invalid max topology index")
        cls.topologies[max_top]=[]
        for i in range(len(diagrams)-1, id-1, -1):
            cls.topologies[diagrams[i].topology_idx].remove(diagrams[i])
            diagrams[i].topology_idx += 1
            cls.topologies[diagrams[i].topology_idx].append(diagrams[i])
        if not cls.topologies[diagrams[id].topology_idx][0].topology_owner:
            cls.topologies[diagrams[id].topology_idx][0].topology_owner = True
        cls.map_id = {}
        for i in range(0, len(diagrams)):        
            cls.map_id[diagrams[i].uid]=i
        cls.regions.remap_reg_from = diagrams[id-1]
        cls.regions.remap_reg_to = diagrams[id]

    @classmethod
    def fix_topologies(cls, diagrams):
        """check and fix topologies ordering"""
        max_top=0
        copy_to=0
        for i in range(0, len(diagrams)):
            if diagrams[i].topology_idx!=max_top:
                if len(cls.topologies[max_top])>0:
                    copy_to += 1
                    max_top = diagrams[i].topology_idx
                if copy_to != max_top:
                    cls.topologies[diagrams[i].topology_idx].remove(diagrams[i])
                    if not copy_to in cls.topologies:
                        cls.topologies[copy_to] = []
                    diagrams[i].topology_idx = copy_to
                    cls.topologies[copy_to].append(diagrams[i])
        cls.map_id = {}
        for i in range(0, len(diagrams)):
            if cls.topologies[diagrams[i].topology_idx].index(diagrams[i])==0:
                diagrams[i].topology_owner = True
            else:
                diagrams[i].topology_owner = False            
            cls.map_id[diagrams[i].uid]=i
        del_keys = []
        for key in cls.topologies:
            if len(cls.topologies[key])==0:
                del_keys.append(key)
        for key in del_keys:
            if key<=copy_to:
                raise Exception("Empty topology inside structure")
            del cls.topologies[key]

    def __init__(self, topology_idx, global_history): 
        global __next_diagram_uid__
        self.uid = __next_diagram_uid__
        """Unique diagram id"""
        __next_diagram_uid__ += 1  
        self.topology_idx = topology_idx
        """Topology index"""
        self._rect = None
        """canvas Rect"""
        self.points = []
        """list of points"""
        self.topology_owner = False
        """First diagram in topology is topology owner, and is 
        responsible for its saving"""
        if not topology_idx in self.topologies:
            self.topology_owner = True
            self.topologies[topology_idx] = []
        self.topologies[topology_idx].append(self)
        self.lines = []
        """list of lines"""
        self.polygons = []
        """list of polygons"""
        self.new_polygons = []
        """list of polygons that has not still graphic object"""
        self.deleted_polygons = []
        """list of polygons that should be remove from graphic object"""
        self._zoom = 1.0
        """zoom"""
        self.pen = QtGui.QPen(QtCore.Qt.black, 1.4)
        """pen for object paintings"""        
        self.bpen = QtGui.QPen(QtCore.Qt.black, 3.5)
        """pen for highlighted object paintings"""
        self.pen_changed = True
        """pen need be changed"""
        self._recount_zoom = 1.0
        """pen need be changed"""
        self.x = 0
        """x vew possition"""
        self.y = 0 
        """y viw possition"""
        self._history = DiagramHistory(self, global_history)
        """history"""
        self.po = PolygonOperation()
        """Help variable for polygons structures"""
        
    def join(self):
        """Add diagram to topologies"""
        self.topology_owner = False
        if not self.topology_idx in self.topologies:
            self.topology_owner = True
            self.topologies[self.topology_idx] = []
        self.topologies[self.topology_idx].append(self)
        
    def release(self):
        """Discard this object from global links"""
        self.topologies[self.topology_idx].remove(self)
        if len(self.topologies[self.topology_idx])<1:
            del self.topologies[self.topology_idx]
        else:
            self.topologies[self.topology_idx][0].topology_owner = True
        
    def dcopy(self):
        """My deep copy implementation"""
        ret = Diagram(self.topology_idx, self._history.global_history)
        
        for point in self.points:
            ret.add_point(point.x, point.y, 'Copy point', None, True)
        for line in self.lines:
            ret.join_line(ret.points[self.points.index(line.p1)],
                ret.points[self.points.index(line.p2)],
                "Copy line", None, True)
        ret.x = self.x
        ret.y = self.y
        ret.zoom = self.zoom
            
        return ret
      
    @property
    def rect(self):
        if self._rect is None:
            if self.shp.boundrect is None:
                dx= (abs(self.area.xmax-self.area.xmin)+abs(self.area.ymax-self.area.ymin))/100
                return QtCore.QRectF(self.area.xmin-dx, self.area.ymin-dx, 
                    self.area.xmax-self.area.xmin+2*dx, self.area.ymax-self.area.ymin+2*dx)
            else:
                return self.shp.boundrect
        margin = (self._rect.width()+self._rect.height())/100
        if margin==0:
            margin = 1
        return QtCore.QRectF(
            self._rect.left()-margin, 
            self._rect.top()-margin,
            self._rect.width()+2*margin,
            self._rect.height()+2*margin)
            
    @property
    def zoom(self):
        return self._zoom 
        
    @zoom.setter
    def zoom(self, value):
        """zoom property, if zoom is too different, recount pen width"""        
        self._zoom = value
        ratio = self._recount_zoom/value
        if ratio>1.2 or ratio<0.8:
            self.pen_changed = True
            self.pen = QtGui.QPen(QtCore.Qt.black, 1.4/value)
            self.bpen = QtGui.QPen(QtCore.Qt.black, 3.5/value)
            self._recount_zoom = value
            
    def first_shp_object(self):
        """return if is only one shp object in diagram"""
        if len( self.points)>0:
            return False
        if len( self.lines)>0:
            return False
        if len(self.shp.datas)>1:
            return False
        return True
    
    def get_point_by_id(self, id):
        """return point or None if not exist"""
        for point in self.points:
            if point.id==id:
                return point
        return None

    def get_line_by_id(self, id):
        """return line or None if not exist"""
        for line in self.lines:
            if line.id==id:
                return line
        return None
        
    def find_line(self, p1_id, p2_id):
        """Find line accoding points index"""
        p1 = self.points[p1_id]
        p2 = self.points[p2_id]
        for line in p1.lines:
            if line in p2.lines:
                return line
        return None
        
        
    def add_file(self, file):
        """Add new shapefile"""
        disp = self.shp.add_file(file)
        self.recount_canvas()
        return disp

    def recount_canvas(self):
        """recount canvas size"""
        self._rect = self.shp.boundrect        
        for p in self.points:
            if self._rect is None:
                self._rect = QtCore.QRectF(p.x, p.y, 0, 0)   
            else:
                if self._rect.left()>p.x:
                    self._rect.setLeft(p.x)
                if self._rect.right()<p.x:
                    self._rect.setRight(p.x)
                if self._rect.top()>p.y:
                    self._rect.setTop(p.y)            
                if self._rect.bottom()<p.y:
                    self._rect.setBottom(p.y)
                    
    def add_polygon(self, lines, label=None, not_history=True, copy=None):
        """Add polygon to list"""
        polygon = Polygon(lines)
        self.polygons.append(polygon)
        if not not_history:
            if copy is not None:
                self.regions.copy_regions(2, polygon.id, copy.id, not not_history, label)
            else:
                self.regions.add_regions(2, polygon.id, not not_history, label)
        self.new_polygons.append(polygon)        
        return polygon
        
    def del_polygon(self, polygon, label=None, not_history=True):
        """Remove polygon from list"""
        self.polygons.remove(polygon)
        for line in polygon.lines:
            line.del_polygon(polygon)
        if not not_history:
            self.regions.del_regions(2, polygon.id, not not_history, label)
        self.deleted_polygons.append(polygon)
        
    def add_point(self, x, y, label='Add point', id=None, not_history=False):
        """Add point to canvas"""
        point = Point(x, y, id)
        self.points.append(point) 
        self.po.add_point(self, point) 
        #save revert operations to history
        if not not_history:
            self.regions.add_regions(0, point.id)
            self._history.delete_point(point.id, label)
        # recount canvas size
        if self._rect is None:
            self._rect = QtCore.QRectF(x, y, 0, 0)        
        else:
            if self._rect.left()>x:
                self._rect.setLeft(x)
            if self._rect.right()<x:
                self._rect.setRight(x)
            if self._rect.top()>y:
                self._rect.setTop(y)            
            if self._rect.bottom()<y:
                self._rect.setBottom(y)
        return point
        
    def add_point_id(self, x, y):
        """Add point to canvas and return index"""
        point = Point(x, y, id)
        self.points.append(point) 
        # recount canvas size
        if self._rect is None:
            self._rect = QtCore.QRectF(x, y, 0, 0)        
        else:
            if self._rect.left()>x:
                self._rect.setLeft(x)
            if self._rect.right()<x:
                self._rect.setRight(x)
            if self._rect.top()>y:
                self._rect.setTop(y)            
            if self._rect.bottom()<y:
                self._rect.setBottom(y)
        return self.points.index(point)
        
    def import_decomposition(self, decomposition):
        """Save decomposition and reload lines and polygons"""
        self.po.set_new_decomposition(self, decomposition)
    
    def move_point(self, p, x, y, label='Move point', not_history=False):
        """Add point to canvas"""
        #save revert operations to history
        if not not_history:
            self._history.move_point(p.id, p.x, p.y, label)
        # compute recount params
        need_recount = False
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if (not trimed.contains(p.qpointf())) or \
            (not self._rect.contains(QtCore.QPointF(x, y))):
            need_recount = True
        # move point
        p.x = x
        p.y = y        
        # recount canvas size
        if need_recount:
            self.recount_canvas()
            
    def delete_point(self, p, label='Delete point', not_history=False):
        assert len(p.lines)==0
        #save revert operations to history
        if not not_history:
            self._history.add_point(p.id, p.x, p.y, label)
        # compute recount params
        need_recount = False
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if not trimed.contains(p.qpointf()) :
            need_recount = True
        # remove point
        self.po.remove_point(self, p) 
        self.points.remove(p)
        if not not_history:
            self.regions.del_regions(0, p.id, not not_history)
        # recount canvas size
        if need_recount:
            self.recount_canvas()

    def join_line(self,p1, p2, label=None, id=None, not_history=False):
        """Add line from point p1 to p2"""
        assert p1 != p2
        if p1>p2:
            pom = p1
            p1 = p2
            p2 = pom
        for line in p1.lines:
            if line.p2 == p2:
                return line
        line = Line(p1, p2, id)
        p1.lines.append(line)
        p2.lines.append(line)
        self.lines.append(line)        
        #save revert operations to history
        if not not_history:
            self._history.delete_line(line.id, label)        
        self.po.add_line(self, line, None, not_history) 
        if not not_history:
            self.regions.add_regions(1, line.id, not not_history)
        return line
        
    def join_line_import(self,p1_id, p2_id, segment):
        """Import line from point p1 to p2"""
        p1 = self.points[p1_id]
        p2 = self.points[p2_id]
        if p1>p2:
            pom = p1
            p1 = p2
            p2 = pom        
        line = Line(p1, p2)
        line.segment = segment
        p1.lines.append(line)
        p2.lines.append(line)
        self.lines.append(line)        
        return line
        
    def join_line_intersection(self, p1, p2, label=None):
        """
        As Join line, but try add lines created by intersection
        return added_points, moved_points, added_lines
        """
        new_points, new_lines = PolygonOperation.try_intersection(self, p1, p2, label)
        lines = []
        temp_p = p1
        for p in new_points:
            lines.append(self.join_line(temp_p, p, label))
            temp_p = p
        lines.append(self.join_line(temp_p, p2, label))
        lines.extend(new_lines)
        return new_points, new_points, lines
        
    def delete_line(self, l, label="Delete line", not_history=False):
        """remove set line from lines end points"""
        self.lines.remove(l)
        l.p1.lines.remove(l)
        l.p2.lines.remove(l)
        self.po.remove_line(self, l)
        #save revert operations to history
        if not not_history:
            self._history.add_line(l.id, l.p1.id, l.p2.id, label)
            self.regions.del_regions(1, l.id, not not_history)        
    
    def move_point_after(self, p, x_old, y_old, label='Move point'):
        """Call if point is moved by another way and need save history and update polygons"""
        #save revert operations to history
        self._history.move_point(p.id, x_old, y_old, label)
        # compute recount params
        small = (self._rect.width()+self._rect.height())/1000000
        trimed = self._rect - QtCore.QMarginsF(small, small, small, small)
        if (not trimed.contains(QtCore.QPointF(x_old, y_old))) or \
            (not self._rect.contains(p.qpointf())):
            self.recount_canvas()
        
    def add_line(self,p, x, y, label='Add line', no_history=False):
        """Add line from point p to [x,y]"""
        p2 = self.add_point(x, y, label, None, no_history)
        return p2, self.join_line(p, p2, None, None, no_history)
        
    def add_new_point_to_line(self, line, x, y, label='Add new point to line'):
        """Add new point to line and split it """
        xn, yn = self.get_point_on_line(line, x, y)
        self.po.split_line(self, line)
        p = self.add_point(xn, yn, label)
        p.lines.append(line)
        line.p2.lines.remove(line)
        point2 = line.p2
        line.p2 = p
        line.object.refresh_line()
        l2 = self.join_line(point2, line.p2, None)
        #save revert operations to history        
        self._history.add_line(line.id, line.p1, point2, None)
        self._history.delete_line(line.id, None)        
        return p, l2
        
    def add_point_to_line(self, line, point, label='Add point to line'):
        """
        Add point to line and split it. Return new line and array of lines that should be removed.
        This lines is released from data, but object is existed, and should be relesed after discarding
        graphic object.
        """
        releasing_lines = []
        xn, yn = self.get_point_on_line(line, point.x, point.y)
        self.move_point(point, xn, yn, label)
        point.lines.append(line)
        line.p2.lines.remove(line)
        point2 = line.p2        
        line.p2 = point
        line.object.refresh_line()
        l2 = self.join_line(point, point2)        
        #save revert operations to history
        self._history.add_line(line.id, line.p1.id, point2.id, None)
        self._history.delete_line(line.id, None)
        # TODO: case if one line is merged (line between new point and one of line point)
        # TODO: case if two lines is merged (triangle) 
        

        return l2, releasing_lines
        
    def merge_point(self, point, atached_point, label='Merge Points'):
        """
        Merge two points. Atached_point will be remove from data
        and shoud be released after discarding graphic object.
        Return array of lines that should be removed. This lines is 
        released from data, but object is existed, and should be relesed 
        after discarding graphic object.
        """
        releasing_lines = []
        # move all lines from atached_point to point
        for line in atached_point.lines:
            if line in point.lines:
                # line between point and atached_point
                assert (line.p1== point and line.p2 == atached_point) or \
                    (line.p2 == point and line.p1 == atached_point)
                releasing_lines.append(line)
                self.delete_line(line, label)
                label = None
                continue
            p = None            
            if line.p1== atached_point:
                p = line.p1
            else:
                assert line.p2== atached_point
                p = line.p2
            for mline in point.lines:
                if (mline.p1== p) or (mline.p2==p):
                    # exist two lines between: p - atached_point and 
                    # the p - point ₌> merge this lines
                    releasing_lines.append(line)
                    self.delete_line(line, label)
                    label = None
                    p=None
                    break
            if p is not None:
                # move line from atached_point to point
                objekt = line.object
                id = line.id
                self.delete_line(line, label)
                label = None
                if p == line.p1:
                    line.p1 = point
                else:
                    line.p2 = point
                line = self.join_line(line.p1, line.p2, label, id)
                line.object = objekt                
        # remove point 
        self.delete_point(atached_point, label)
        return releasing_lines
        
    def try_delete_point(self, p, label="Delete point"):
        """Try remove set point, and return it 
        if point is in some line return False"""
        if len(p.lines)>0:
            return False
        self.delete_point(p, label)
        return True
    
    @staticmethod
    def make_tmp_line(p1x, p1y, p2x, p2y):
        """Make temporrary line"""
        p1 = Point(p1x, p1y)
        p2 = Point(p2x, p2y)
        line = Line(p1,p2)
        p1.lines.append(line)
        p2.lines.append(line)
        return line
        
    @staticmethod
    def get_point_on_line(line, px, py):
        """Compute point on line"""
        dx = line.p2.x-line.p1.x
        dy = line.p2.y-line.p1.y 
        if dx>dy:
            return px, line.p1.y + (px-line.p1.x)*dy/dx
        return line.p1.x + (py-line.p1.y)*dx/dy, py
