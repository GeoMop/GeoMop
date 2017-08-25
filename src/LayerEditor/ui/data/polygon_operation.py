import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import abc
from enum import IntEnum
from copy import deepcopy

class LinePlace(IntEnum):
    """Place, where is was joined line"""
    boundary = 0
    """Line is part of shape boundary"""
    bundled = 1
    """Line is attached to shape boundary"""
    cluster = 2
    """Line is  in shape"""
    

class Polyline():
    """
    One polyline and its operation
    """
    def __init__(self, line=None):
        if line==None:
            self.lines = []
            self.points = []
        else:            
            self.lines = [line]
            """polyline parts"""
            self.points = [line.p1, line.p2]
            """polyline ordered points"""
        
    def split(self, p):
        """
        Split polyline amd return end as new polyline
        or None
        """
        for i in range(0, len(self.points)):
            if self.points[i] == p:
                new_poly = Polyline()
                new_poly.lines[i:]
                new_poly.points[i:]
                self.lines[0:i]
                self.points[0:i+1]
                return new_poly
        return None
        
    def join(self, polyline):
        """Join two polylines. One of polyline points must be 
        same as self end point"""
        if self.points[-1]==polyline.points[0]:
            self.lines.extend(polyline.lines)
            self.points.extend(polyline.points[1:])
        else:
            self.lines.extend(polyline.lines.reverse())
            self.points.extend(polyline.points[1:].reverse())            
        
class PolylineCluster():
    """
    Cluster of bundled polylines
    """
    def __init__(self, first_line, join=None):
        self.polylines = [Polyline(first_line)]
        """Bundled polylines"""
        self.bundles = []
        """Polyline joins (Points)"""
        self.joins = []
        """Points, that is line join with shape. (None -> line is not join)"""
        self.split_polygon = False
        """Some budled cluster have two joins, try split polygon"""
        self.check_inner_polygons = False
        """Polygon border should be reloaded"""
        self.cyrcle_poly = None
        """Polyline that should be get to polygon"""
    
    def get_point(self):
        """Return first found point"""
        if len(self.boundary_points)>0:
            return self.boundary_points[0]
        if len(self.bundled_clusters)>0:
            return self.bundled_clusters.polyline[0].points[0]
        return self.bundled.polyline[0].points[0]
        
    def set_possition(self, polygon, bundled):
        """All line set in polygon"""
        for poly in self.polyline:
            for line in poly.lines:
                line.in_polygon = polygon
                line.bundled = True
        for poly in self.polyline:
            for line in poly.lines:
                line.in_polygon = polygon
                line.bundled = False
        
    def set_bundled(self, bundled):
        """All line set in polygon"""
        for poly in self.polyline:
            for line in poly.lines:
                line.bundled = True
        for poly in self.polyline:
            for line in poly.lines:
                line.bundled = False
        
    def reduce_polylines(self):
        """Return only polylines, that both end points continue"""
        counter = [0]*len(self.bundles)
        bundles = deepcopy(self.bundles)
        for join  in self.joins:
            bundles.append(self.join)
            counter.append(1)
        res = []
        # romove all lines, that is not in bundle and prepare counter
        for poly in self.polylines:
            if not poly.points[0] in bundles or \
                not poly.points[-1] in bundles:
                continue
            res.append(poly)
            counter[bundles.index(poly.points[0])] += 1
            counter[bundles.index(poly.points[-1])] += 1
        end = False
        while not end:
            end = True
            remove = []
            for poly in res:
                if counter[bundles.index(poly.points[0])]<2 or \
                    counter[bundles.index(poly.points[-1])]<2:
                    remove.append(poly)
                    counter[bundles.index(poly.points[0])] -= 1
                    counter[bundles.index(poly.points[-1])] -= 1
                    end = False
            for poly in remove:
                res.remove(poly)
        return res
        
    def try_add_in_bundle(self, p, line):
        """Try add line to bundle in point p"""
        for bundle in self.bundles:                        
            if p==bundle:
                self.polylines.append(Polyline(line))
                return True
        return False
        
    def try_split_by_bundle(self, p, line, only_split=False):
        """Try split polyline by boundle and add new polyline"""
        for poly in self.polylines:  
            new_poly = poly.split(p)
            if new_poly is not None:
                self.polylines.append(new_poly)
                if not only_split:
                    self.polylines.append(Polyline(line))
                self.bundles.append(p)
                return True
        return False
        
    def contains_line(self, line):
        """Try add line to end of polyline"""
        for poly in self.polylines:
            for pline in poly.lines:
                if line == pline:
                    return True
        return False
        
    def find_poly_by_end_point(self, line):
        """Find polyline with set end point"""
        for poly in self.polylines:
            if poly.points[-1]:
                return poly
        return None 
 
    def is_point_bundle(self, p):
        """Find polyline with set end point"""
        for bundle in self.bundles:                        
            if p==bundle:
                return True
        return False         
    
    def try_add_to_poly_end(self, p, line):
        """Try add line to end of polyline"""
        for poly in self.polylines:
            if poly.points[0]==p:
                if p in self.bundles:
                    raise Exception("Invalid end polyline point.")
                poly.points.insert(0, line.second_point(p))
                poly.lines.insert(0, line)
                return True
            if poly.points[-1]==p:
                if p in self.bundles:
                    raise Exception("Invalid end polyline point.")
                poly.points.append(line.second_point(p))
                poly.lines.append(line)
                return True
        return False                    
                    
class Shape(metaclass=abc.ABCMeta):
    """
    Polygon or outside ancestor
    """
    
    def __init__(self):
        self.clusters = []
        """Polyline clusters that is in shape"""
        self.boundary_lines = []
        """lines in boundary"""
        self.boundary_points = []
        """points in boundary"""
        self.bundled_clusters = []
        """lines that is bundled to boundary"""
        self.reload_polygon = False
        """Polygon border should be reloaded"""
    
    def find_cluster(self, line):
        """Return if cluster is bunded and cluster index"""
        for i in range(0, len(self.bundled_clusters)):
            if self.bundled_clusters[i].contains_line(line):
                return True, i
        for i in range(0, len(self.clusters)):
            if self.clusters[i].contains_line(line):
                return False, i
                
    def join(self, line):
        """Join line in shape, return if is bundled"""
        res = True
        for l in line.p1.lines:
            if l!=line:
                neighbor1 = l
                break
        for l in line.p2.lines:
            if l!=line:
                neighbor2 = l
                break
        if not neighbor1.bundled:
            cluster = self._append_in_polygon(len(line.p1.lines), line.p1, line)
            if cluster is None:
                raise Exception("Can't join line in polygon structures")
            if not neighbor2.bundled:
                if not self._join_two_clusters(
                    cluster, len(line.p2.lines), line.p2, line):
                    raise Exception("Can't join line in polygon structures")
                res = False
            else:
                if not self._join_cluster_with_boundary(
                    cluster, len(line.p2.lines), line.p2, line):
                    raise Exception("Can't join line in polygon structures")
        elif not neighbor2.bundled:
            cluster = self._append_in_polygon(len(line.p2.lines), line.p2, line)
            if cluster is None:
                raise Exception("Can't join line in polygon structures")
            if not self._join_cluster_with_boundary(
                cluster, len(line.p1.lines), line.p1, line):
                raise Exception("Can't join line in polygon structures")
        else:
            cluster = self._append_to_boundary(len(line.p1.lines), line.p1, line)
            if cluster is None:
                raise Exception("Can't join line in polygon structures")
            if not self._join_two_boundary(
                cluster, len(line.p2.lines), line.p2, line):
                raise Exception("Can't join line in polygon structures") 
        return res
    
    def append(self, line):
        """append line to shape, return if is bundled"""
        res = True
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>1:
            p = line.p1
            lp = lp1 
        else:
            p = line.p2
            lp = lp2
        for l in p.lines:
            if l!=line:
                neighbor = l
                break
        if not neighbor.bundled:
            appended = self._append_in_polygon(lp, p, line) is not None 
            res = False
        else:
            appended = self._append_to_boundary(lp, p, line) is not None
            self.reload_polygon = True
        if not appended:
            raise Exception("Can't add line to polygon structures")
        return res
        
    def _make_cyrcle(self, cluster1, cluster2, p):
        """Try make polygon by polyline"""
        polyline = cluster1.find_poly_by_end_point(p)
        if polyline.points[0]==p:
            cluster1.cyrcle_poly = polyline
        cluster1.check_inner_polygons = True
        
    def _join_clusters(self, cluster1, cluster2, bundled1, bundled2):
        """Join two cluster, join point must be prepered before
        this function calling"""
        if not bundled1 and bundled2:
            tmp = cluster1
            cluster1 = cluster2
            cluster2 = tmp
            tmp = bundled1
            bundled1 = bundled2
            bundled2 = tmp             
        if bundled2:
            self.bundled_clusters.remove(cluster2)
        else:
            self.clusters.remove(cluster2)
        cluster2. set_bundled(True)
        cluster1.bundles.extend(cluster2.bundles)
        cluster1.polylines.extend(cluster2.polylines)
        if bundled1:
            if bundled2:
                cluster1.joins.extend(cluster2.joins)
                cluster1.split_polygon = True
            else:
                self.reload_polygon = True        
        
    def _join_two_boundary(self, cluster, lp, p, line):
        """Join two boundary clusters"""
        joined = False            
        #try join to boundary
        if lp>2:
            for bp in self.boundary_points:
                if p==bp:
                    self.joins.append(p)
                    cluster.split_polygon = True
                    joined = True
                    break                    
        if not joined:
            if lp>3:
                #try join to bundled in bundle
                for bcluster in self.bundled_clusters:
                    if bcluster.is_point_bundle(p):
                        if bcluster==cluster:
                            self._make_cyrcle(bcluster, cluster, p)
                        else:
                            self._join_clusters(bcluster, cluster, True, True)
                        joined = True
            elif lp==3:
                #try split to bunded polyline in cluster and make new bundle
                for bcluster in self.bundled_clusters:
                    if bcluster.try_split_by_bundle(p, line, True):
                        if bcluster==cluster:
                            self._make_cyrcle(bcluster, cluster, p)
                        else:
                            self._join_clusters(bcluster, cluster, True, True)
                        joined = True
            elif lp==2:
                #try add to end bounded cluster
                polyline = cluster.find_poly_by_end_point(p)
                for bcluster in self.bundled_clusters:                                        
                    bpolyline = bcluster.find_poly_by_end_point(p)
                    if bpolyline is not None:                        
                        cluster.polylines.remove(polyline)
                        bpolyline.join(polyline)
                        self._join_clusters(bcluster, cluster, True, True)
                        joined = True
                        break
        return joined
        
    def _join_cluster_with_boundary(self, cluster, lp, p, line):
        """Join cluster with boundary clusters"""
        joined = False            
        #try join to boundary
        if lp>2:
            for bp in self.boundary_points:
                if p==bp:
                    self.clusters.remove(cluster)
                    self.bundled_clusters.append(cluster)
                    self.joins.append(p)
                    self.reload_polygon = True
                    joined = True
                    break                    
        if not joined:
            if lp>3:
                #try join to bundled in bundle
                for bcluster in self.bundled_clusters:
                    if bcluster.is_point_bundle(p):
                        self._join_clusters(bcluster, cluster, True, False)
                        joined = True
            elif lp==3:
                #try split to bunded polyline in cluster and make new bundle
                for bcluster in self.bundled_clusters:
                    if bcluster.try_split_by_bundle(p, line, True):
                        self._join_clusters(bcluster, cluster, True, False)
                        joined = True
            elif lp==2:
                #try add to end bounded cluster
                polyline = cluster.find_poly_by_end_point(p)
                for bcluster in self.bundled_clusters:                                        
                    bpolyline = bcluster.find_poly_by_end_point(p)
                    if bpolyline is not None:
                        cluster.polylines.remove(polyline)
                        bpolyline.join(polyline)
                        self._join_clusters(bcluster, cluster, True, False)
                        joined = True
                        break
        return joined
        
    def _join_two_clusters(self,cluster, lp, p, line):
        """Join two clusters"""
        joined = False            
        #try join to boundary
        if lp>3:
            #try join to bundled in bundle
            for ncluster in self.clusters:
                if ncluster.is_point_bundle(p):
                    if ncluster==cluster:
                        self._make_cyrcle(ncluster, cluster, p)
                    else:
                        self._join_clusters(ncluster, cluster, False, False)
                    joined = True
        elif lp==3:
            #try split to bunded polyline in cluster and make new bundle
            for ncluster in self.clusters:
                if ncluster.try_split_by_bundle(p, line, True):
                    if ncluster==cluster:
                        self._make_cyrcle(ncluster, cluster, p)
                    else:
                        self._join_clusters(ncluster, cluster, False, False)
                    joined = True
        elif lp==2:
            #try add to end bounded cluster
            polyline = cluster.find_poly_by_end_point(p)
            for ncluster in self.clusters:                                        
                npolyline = ncluster.find_poly_by_end_point(p)
                if npolyline is not None:
                    if ncluster==cluster:
                        if npolyline!=polyline:
                            cluster.polylines.remove(polyline)
                            npolyline.join(polyline)
                            if  npolyline.points[-1]==npolyline.points[0]: 
                                cluster.cyrcle_poly = npolyline
                        else:
                            cluster.cyrcle_poly = npolyline
                        cluster.check_inner_polygons = True
                    else:
                        cluster.polylines.remove(polyline)
                        npolyline.join(polyline)
                        self._join_clusters(ncluster, cluster, False, False)
                    joined = True
                    break
        return joined
        
    def _append_to_boundary(self, lp, p, line):
        """append line to polygon boundary"""
        res_cluster = None            
        #try add to boundary
        if lp>2:
            for bp in self.boundary_points:
                if p==bp:
                    res_cluster = PolylineCluster(line, p)
                    self.bundled_clusters.append(res_cluster)
                    break                    
        if res_cluster is None:
            if lp>3:
                #try add to bundled in bundle
                for cluster in self.bundled_clusters:
                    if cluster.try_add_in_bundle(p, line):
                        res_cluster = cluster
                        break
            elif lp==3:
                #try split to bunded cluster in bundle
                for cluster in self.bundled_clusters:
                    if cluster.try_split_by_bundle(p, line):
                        res_cluster = cluster
                        break
            elif lp==2:
                #try add to end bounded cluster
                for cluster in self.bundled_clusters:
                    if cluster.try_add_to_poly_end(p, line):
                        res_cluster = cluster
                        break
        return res_cluster

        
    def _append_in_polygon(self, lp, p, line):
        """append line in polygon"""
        res_cluster = None 
        if lp>3:
            #try add to cluster in bundle
            for cluster in self.clusters:
                if cluster.try_add_in_bundle(p, line):
                    res_cluster = cluster
                    break
        elif lp==3:
            #try split to cluster in bundle
            for cluster in self.clusters:
                if cluster.try_split_by_bundle(p, line):
                    res_cluster = cluster
                    break                        
        elif lp==2:
            #try split to cluster in bundle
            for cluster in self.clusters:
                if cluster.try_add_to_poly_end(p, line):
                    res_cluster = cluster
                    break
        return res_cluster
        
    @abc.abstractmethod    
    def apply_add_line_changes(self, diagram, polygon, line):    
        """apply all changes after one operation"""
        pass        
    
    def add(self, line):
        """add line to shape variables, return if is bundled"""
        self.clusters.append(PolylineCluster(line)) 
        return False
        
    
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
        
    def _find_path(self, path, polylines, start_point, end_point):
        """Try recursivly find path to set point"""
        for poly in polylines:
            found = False
            if poly.points[0]==start_point:
                if poly.points[-1]==end_point:
                    path.append(poly)
                    return path
                found = True
            if poly.points[-1]==start_point:
                if poly.points[0]==end_point:
                    path.append(poly)
                    return path
                found = True
            if found:
                new_polylines = deepcopy(polylines)
                new_path = deepcopy(path)
                new_polylines.remove(poly)
                new_path.append(poly)
                if poly.points[0]==start_point:
                    res = self._find_path(new_path, new_polylines, poly.points[-1], end_point)
                else:
                    res = self._find_path(new_path, new_polylines, poly.points[0], end_point)
                if res is not None:
                    return res
            return None
            

class Outside(Shape):
    """
    Shape outside polygons
    """
    
    def __init__(self):
        super(Outside, self).__init__()          

    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    def take(self, line):
        """take away line from shape"""
        pass
    
    def remove(self, line):
        """remove line from shape"""
        pass 
    
    def _find_line_in_polylines(self, polylines, line):
        """Find polyline containing set line in polylines list"""
        for polyline in polylines:
            if line in polyline.lines:
                return polyline
        return None
        
    def apply_add_line_changes(self, diagram, polygon, line):    
        """apply all changes after one operation"""
        split = False
        for cluster in self.clusters:
            if cluster.split_polygon:
                split = True
            if cluster.check_inner_polygons:
                if cluster.cyrcle_poly is not None:
                    self.make_polygon_from_cyrcle(diagram, cluster, cluster.cyrcle_poly)
                    cluster.cyrcle_poly = None
                else:
                    polylines = cluster.reduce_polylines()
                    start_polyline = self._find_line_in_polylines(polylines, line)
                    path = self._find_path([start_polyline], polylines, 
                        start_polyline.points[0], start_polyline.points[-1])
                    if len(path)>1:
                        self.make_polygon_from_path(diagram, path)
                cluster.check_inner_polygons = False
        if not split:
            for cluster in self.bundled_clusters:
                if cluster.split_polygon:
                    split = True
        if split:
            polylines = []
            used_clusters = []
            for cluster in self.bundled_clusters:
                if len(cluster.joins)>1:
                    polylines.extend(cluster.reduce_polylines())
                    used_clusters.apped(cluster)
            for line in self.boundary:
                polylines.append.Polyline(line)
            for polyline in polylines:
                new_polylines = deepcopy(polylines)
                new_polylines.remove(polyline)
                path = self._find_path([polyline], new_polylines, polyline.points[0], polyline.points[-1])
                if len(path)>1:
                    break
            if len(path)>1:
                self.make_polygon(diagram, used_clusters, path)
                
    def make_polygon_from_path(self, diagram, path):
        """Make polygon from path"""
                
    def make_polygon_from_cyrcle(self, diagram, cluster, polyline):
        """Make polygon from path"""
        p = polyline.points[0]
        polygon = diagram.add_polygon(polyline.lines)
        polygon.spolygon = SimplePolygon()
        polygon.spolygon.gtpolygon = QtGui.QPolygonF()        
        for p in polyline.points:
            polygon.spolygon.gtpolygon.append(p.qpointf())
        for l in polyline.lines:
            if l.polygon2 is None:
                self.boundary_lines.append(l)
                self.boundary_points.append(l.p1)
        polygon.spolygon.boundary_lines = polyline.lines
        polygon.spolygon.boundary_points = polyline.points
        is_bundled = cluster in self.bundled_clusters
        cluster.polylines.remove(polyline)
        if len(cluster.polylines)==0:
            if is_bundled:
                self.bundled_clusters.remove(cluster)
            else:
                self.clusters.remove(cluster)
        else:
            cluster.joins.append(p)
            polyline = cluster.polylines[0]
            if polyline.points[0] == p:
                test_point = polyline.points[1]
            else:
                test_point = polyline.points[0]
            if polygon.spolygon.gtpolygon.containsPoint(test_point.qpointf(), QtCore.Qt.OddEvenFill):
                #TODO process inner objects
                if is_bundled:
                    self.bundled_clusters.remove(cluster)
                else:
                    self.clusters.remove(cluster)                                
                polygon.spolygon.bundled_clusters.append(cluster)
                cluster.set_possition(polygon, True)
            else:
                if not is_bundled:
                    self.clusters.remove(cluster)                
                    self.bundled_clusters.append(cluster)
        for cluster in self.bundled_clusters:
            if polygon.spolygon.gtpolygon.containsPoint(cluster.get_point().qpointf(), QtCore.Qt.OddEvenFill):
                #TODO process inner objects
                self.bundled_clusters.remove(cluster)
                polygon.spolygon.bundled_clusters.append(cluster)
                cluster.set_possition(polygon)
        for cluster in self.clusters:
            if polygon.spolygon.gtpolygon.containsPoint(cluster.get_point().qpointf(), QtCore.Qt.OddEvenFill):
                self.bundled_clusters.remove(cluster)
                polygon.spolygon.bundled_clusters.append(cluster)
                cluster.set_possition(polygon)
        
   
class SimplePolygon(Shape):
    """
    Polygon without bundled polyline
    """
    
    def __init__(self):
        super(SimplePolygon, self).__init__()
        self.gtpolygon = None
        """Qt polygon"""

    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    def take(self, line):
        """take away line from shape"""
        pass
    
    def remove(self, line):
        """remove line from shape"""
        pass
        
    def apply_add_line_changes(self, diagram, polygon, line):    
        """apply all changes after one operation"""
        for cluster in self.bundled_clusters:
            if cluster.split_polygon:
                polylines = cluster.reduce_polylines()
                for poly in polylines:
                    if poly.points[0]==cluster.joins[0] or \
                        poly.points[-1]==cluster.joins[0]:
                        new_polylines = deepcopy(polylines)
                        new_polylines.remove(poly)
                        if poly.points[0]==cluster.joins[0]:
                            path = self._find_path([poly], new_polylines, poly.points[-1], 
                                cluster.joins[1])
                        else:
                            path = self._find_path([poly], new_polylines, poly.points[0], 
                                cluster.joins[1])
                        break
                        
            if len(path)>1:
                break
        if len(path)>1:
           self._split_polygon_by_path(diagram, cluster, path)
        if self.reload_polygon:
            # TODO:
            pass

    def make_polygon_from_path(self, diagram, path):
        """Make polygon from path"""
        
    def make_polygon_from_cyrcle(self, diagram, cluster, polyline):
        """Make polygon from path"""        
        
    def reload_polygon_boundary(self, polygon):
        """Reload polygon boundary in diagram polygon"""

    def split_polygon_by_path(diagram, cluster, path):
        """Split polygon by cluster in set path"""
        pass
        
    def split_polygon_by_cyrcle(diagram, cluster, polyline):
        """Split polygon by cluster in set path"""
        pass


class PolygonOperation():
    """
    Static class for polygon localization
    """
    
    outside = Outside()
    """Shape outside polygons"""
    
    @classmethod
    def find_polygon(cls, diagram, point):
        """Try find polygon that contains point"""
        for polygon in diagram.polygons:
            if polygon.spolygon.gtpolygon.containsPoint(point, QtCore.Qt.OddEvenFill):
                return polygon
        return None
        
    @classmethod
    def find_polygon_by_neighbors(cls, diagram, line, p1, p2):
        """
        Try find polygon in neighboring lines
        
        :param Point p1: Point for neighbors localization
        :param QPointF p2: Point in diagram
        """
        for l in p1.lines:
            if line != l:
                if l.in_polygon is not None:
                    return l.in_polygon
                if l.polygon1 is not None:
                    if l.polygon1.spolygon.gtpolygon.containsPoint(p2, QtCore.Qt.OddEvenFill):
                        return l.polygon1
                if l.polygon2 is not None:
                    if l.polygon2.spolygon.gtpolygon.containsPoint(p2, QtCore.Qt.OddEvenFill):
                        return l.polygon2            
        return None
                
    @classmethod
    def find_polygon_boundary(cls, line):
        """Try find polygon that contains line"""
        return None
    
    @classmethod
    def update_polygon_add_line(cls, diagram, line):
        """Update polygon structures after add line"""
        bundled = False
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>1 and lp2>1:
            middle = QtCore.QPointF(
                (line.p1.x+line.p2.x)/2,(line.p1.y+line.p2.y)/2)                
            polygon = cls.find_polygon_by_neighbors(diagram, line, line.p1, middle)
            if polygon is None:
                bundled = cls.outside.join(line)                
            else:
                bundled = polygon.spolygon.join(line)
        elif lp1>1 or lp2>1:
            if lp1>1:
                p1 = line.p1
                p2 = QtCore.QPointF( line.p2.x, line.p2.y)
            else:
                p1 = line.p2
                p2 = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon_by_neighbors(diagram, line, p1, p2)
            if polygon is None:
                bundled = cls.outside.append(line)
            else:
                bundled = polygon.spolygon.append(line)
        else:
            p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(diagram, p)
            if polygon is None:
                bundled = cls.outside.add(line)                
            else:
                bundled = polygon.spolygon.add(line)
        line.bundled = bundled
        if polygon is None:
            cls.outside.apply_add_line_changes(diagram, None, line)
        else:
            line.in_polygon = polygon
            polygon.spolygon.apply_add_line_changes(diagram, polygon, line)
                
                
        # TODO: If line is in boundary, update outside
                
    
    @classmethod
    def update_polygon_del_line(cls, diagram, line):
        """Update polygon structures after delete line"""
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>1 and lp2>1:
            polygon = cls.find_polygon_boundary(line)
            if polygon is None:
                middle = QtCore.QPointF(
                    (line.p1.x+line.p2.x)/2,(line.p1.y+line.p2.y)/2)                
                polygon = cls.find_polygon(middle)
            if polygon is None:
                cls.outside.disjoin(line)
            else:
                polygon.disjoin(line)
        elif lp1>1 or lp2>1:
            if lp1>1:
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
