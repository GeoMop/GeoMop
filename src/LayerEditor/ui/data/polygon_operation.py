import PyQt5.QtCore as QtCore
import abc

class Polyline():
    """
    One polyline and its operation
    """
    def __init__(self):
        self.lines = []
        """polyline parts"""
        self.gtpolyline = None
        """Qt presentation of polyline"""
        
class Bundle():
    """
    Join of three or more polylines
    """    
    
    def __init__(self, point, line1, line2, line3):
        self.lines[line1, line2, line3]
        """Bundle lines"""
        self.point = point
        """Bundle point"""
        
class PolyLinecluster():
    """
    Cluster of boundled polylines
    """
    def __init__(self):
        self.polylines = []
        """Boundled polylines"""
        self.boundles = []
        """Polyline joins"""

class Shape(metaclass=abc.ABCMeta):
    """
    Polygon or outside ancestor
    """
    
    def __init__(self):
        self.clusters = []
        """Polyline clusters that is join with shape"""
    
    @abc.abstractmethod
    def join(self, line):
        """join line in shape"""
        pass
    
    @abc.abstractmethod
    def append(self, line):
        """append line to shape"""
        pass
    
    @abc.abstractmethod
    def add(self, line):
        """add line to shape variables"""
        pass
    
    @abc.abstractmethod
    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    @abc.abstractmethod
    def take(self, line):
        """take away line from shape"""
        pass
    
    @abc.abstractmethod
    def remove(self, line):
        """remove line from shape"""
        pass
        

class Outside(Shape):
    """
    Shape outside polygons
    """
    
    def __init__(self):
        self.boundary_lines = []
        """lines in boundary"""
        self.boundled_lines = []
        """lines that is boundled to boundary"""

    def join(self, line):
        """join line in shape"""
        pass
    
    def append(self, line):
        """append line to shape"""
        pass
    
    def add(self, line):
        """add line to shape variables"""
        pass
    
    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    def take(self, line):
        """take away line from shape"""
        pass
    
    def remove(self, line):
        """remove line from shape"""
        pass

   
class SimplePolygon(Shape):
    """
    Polygon without boundled polyline
    """
    
    def __init__(self):
        self.gtpolygon = None
        """Qt polygon"""
        self.inner_polygon = []
        """Qt polygon"""

    def join(self, line):
        """join line in shape"""
        pass
    
    def append(self, line):
        """append line to shape"""
        pass
    
    def add(self, line):
        """add line to shape variables"""
        pass
    
    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    def take(self, line):
        """take away line from shape"""
        pass
    
    def remove(self, line):
        """remove line from shape"""
        pass


class PolygonOperation():
    """
    Static class for polygon localization
    """
    
    outside = Outside()
    """Shape outside polygons"""
    
    @classmethod
    def find_polygon(cls, point):
        """Try find polygon that contains point"""
        return None
        
    @classmethod
    def find_polygon_boundary(cls, line):
        """Try find polygon that contains line"""
        return None
    
    @classmethod
    def update_polygon_add_line(cls, diagram, line):
        """Update polygon structures after add line"""
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>0 and lp2>0:
            middle = QtCore.QPointF(
                (line.p1.x+line.p2.x)/2,(line.p1.y+line.p2.y)/2)                
            polygon = cls.find_polygon(middle)
            if polygon is None:
                cls.outside.join(line)
            else:
                polygon.join(line)
        elif lp1>0 or lp2>0:
            if lp1>0:
                p = QtCore.QPointF( line.p2.x, line.p2.y)
            else:
                p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                cls.outside.append(line)
            else:
                polygon.append(line)
        else:
            p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                cls.outside.add(line)
            else:
                polygon.add(line)
        # TODO: If line is in boundary, update outside
                
    
    @classmethod
    def update_polygon_del_line(cls, diagram, line):
        """Update polygon structures after delete line"""
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>0 and lp2>0:
            polygon = cls.find_polygon_boundary(line)
            if polygon is None:
                middle = QtCore.QPointF(
                    (line.p1.x+line.p2.x)/2,(line.p1.y+line.p2.y)/2)                
                polygon = cls.find_polygon(middle)
            if polygon is None:
                cls.outside.disjoin(line)
            else:
                polygon.disjoin(line)
        elif lp1>0 or lp2>0:
            if lp1>0:
                p = QtCore.QPointF( line.p2.x, line.p2.y)
            else:
                p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                cls.outside.take(line)
            else:
                polygon.take(line)
        else:
            p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                cls.outside.remove(line)
            else:
                polygon.remove(line)
                
        
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
        
        return new_points, new_lines
