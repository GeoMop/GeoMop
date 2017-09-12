import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import abc
from enum import IntEnum
from copy import copy

class LinePlace(IntEnum):
    """Place, where is was joined line"""
    boundary = 0
    """Line is part of shape boundary"""
    inner_boundary = 1
    """Line is part of inner shape boundary"""
    bundled = 2
    """Line is attached to shape boundary"""
    cluster = 3
    """Line is  in shape"""
    

class Polyline():
    """
    One polyline and its operation
    """
    
    @staticmethod
    def get_boundary_polyline(blines, bpoints, p1, p2, reverse=False):
        """Get boundary polyline from point p1 to p2"""
        poly = Polyline()
        start = False
        if not reverse:
            for i in range(0, len(bpoints)):
                if bpoints[i]==p1:
                    start=True
                if bpoints[i]==p2 and start:
                    poly.points.append(bpoints[i])
                    return poly
                if start:
                    poly.points.append(bpoints[i])
                    poly.lines.append(blines[i])
            for i in range(0, len(bpoints)):
                if bpoints[i]==p2:
                    poly.points.append(bpoints[i])
                    return poly
                poly.points.append(bpoints[i])
                poly.lines.append(blines[i])                    
        else:
            for i in range(len(bpoints)-1, -1, -1):
                if i==0:
                    line_i = len(bpoints)-1
                else:
                    line_i = i-1
                if bpoints[i]==p1:
                    start=True
                if bpoints[i]==p2 and start:
                    poly.points.append(bpoints[i])
                    return poly
                if start:
                    poly.points.append(bpoints[i])
                    poly.lines.append(blines[line_i])
            for i in range(len(bpoints)-1, -1, -1):
                if i==0:
                    line_i = len(bpoints)-1
                else:
                    line_i = i-1
                if bpoints[i]==p2:
                    poly.points.append(bpoints[i])
                    return poly
                poly.points.append(bpoints[i])
                poly.lines.append(blines[line_i])
        return poly

    
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
                new_poly.lines = self.lines[i:]
                new_poly.points = self.points[i:]
                self.lines = self.lines[0:i]
                self.points = self.points[0:i+1]
                return new_poly
        return None
        
    def join(self, polyline):
        """Join two polylines. One of polyline points must be 
        same as self end point"""
        if self.points[-1]==polyline.points[0]:
            self.lines.extend(polyline.lines)
            self.points.extend(polyline.points[1:])
        else:
            self.lines.extend(polyline.lines[::-1])
            self.points.extend(polyline.points[-2::-1]) 
 
 
class FakePolyline(Polyline):
    """
    Polyline that substitute inner polygon boundaries 
    for simple one line polyline with group variable
    """
    def __init__(self, p1, p2, group_idx):
        line = p1.lines[0].get_tmp_line(p1, p2)
        super(FakePolyline, self).__init__(line)
        self.group_idx = group_idx
 
 
class PolygonGroups(): 
    """
    Cluster of neighbor polygon
    """
    def __init__(self):
        self.groups = []
        """polygon groups"""
        self.polygons = []
        """list of polygons"""
        self.boundaries_lines = []
        """List of groups boundary in order same as groups list"""
        self.boundaries_points = []
        """List of groups boundary in order same as groups list"""
        
    def _make_group_boundary(self, group_id):
        if len(self.boundaries_lines)==group_id:
            self.boundaries_lines.append([])
            self.boundaries_points.append([])
        else:
            self.boundaries_lines[group_id] = []
            self.boundaries_points[group_id] = []            
        polygon = self.groups[group_id][0]
        for line in polygon.boundary_lines:
            if line.count_polygons() == 1:
                start_point = line.p1
                last_point = line.p2
                last_line = line
                self.boundaries_lines[group_id].append(line)
                self.boundaries_points[group_id].append(line.p1)                
                break
        while start_point!=last_point:
            end = True
            for line in last_point.lines:
                if line!=last_line and line.count_polygons() == 1:                    
                    last_line = line
                    self.boundaries_lines[group_id].append(line)
                    self.boundaries_points[group_id].append(last_point)
                    last_point = line.second_point(last_point)
                    end = False
                    break
            if end:
                break
    
    def refresh_polygon(self, polygon):
        for group in self.groups:
            if polygon in group:
                self._make_group_boundary(self.groups.index(group))
                break
    
    def add_polygon(self, polygon):
        self.polygons.append(polygon)
        added = False
        for line in polygon.boundary_lines:                        
            second = polygon.get_second(line)
            if second is not None:
                for group in self.groups:
                    if second in group:
                        group.append(polygon)
                        self._make_group_boundary(self.groups.index(group))
                        added = True
                        break
            if added:
                break
        if not added:
            self.groups.append([polygon])
            self._make_group_boundary(len(self.groups)-1)

    def _find_group(self, point):
        """Find group with set boundary point"""
        for i in range(0, len(self.groups)):
            for p in self.boundaries_points[i]:
                if p==point:
                    return i
                    
    def get_boundary_polyline(self, group_idx, p1, p2, reverse=False):
        """Get boundary polyline from point p1 to p2"""
        return Polyline.get_boundary_polyline(self.boundaries_lines[group_idx], 
            self.boundaries_points[group_idx], p1, p2, reverse)
            
    def _get_fake_path(self, outside, start_point, end_point, paths, clusters):
        """Get polylines path, where is substitute inner polygon boundaries 
        for simple one line polyline withgroup variable. Function try recursivly 
        find list of path to set end_point"""
        group_idx = self._find_group(start_point)
        for cluster in outside.bundled_clusters:
            for join in cluster.inner_joins:
                if join!=end_point and join in self.boundaries_points[group_idx]:
                    polylines = cluster.reduce_polylines()  
                    if len(polylines)==0:
                        continue
                    start_polyline = outside._find_line_in_polylines_point(polylines, join)
                    if cluster==clusters[0]:
                        if start_polyline.points[0]==start_point or \
                            start_polyline.points[-1]==start_point:
                            path = [start_polyline]
                        else:                            
                            path = outside._find_path([], polylines, 
                                join, start_point)                      
                        paths.insert(0, path)
                        clusters.insert(0, cluster)
                        paths.insert(0, FakePolyline(end_point, join, group_idx))
                        return True
                    else: 
                        for next_join in  cluster.inner_joins:
                            if join!=next_join:
                                res = self._get_fake_path(outside, start_point, 
                                    next_join, paths, clusters)
                                if res:
                                    if start_polyline.points[0]==next_join or \
                                        start_polyline.points[-1]==next_join:
                                        path = [start_polyline]
                                    else:
                                        path =outside._find_path([], polylines, 
                                            join, next_join)
                                    paths.insert(0, path)
                                    clusters.insert(0, cluster)
                                    paths.insert(0, FakePolyline(end_point, join, group_idx))
                                return res
        return False
        
    def _get_test_Point(self, point, line):
        """Get point (QPoitF) in half of opposite boundary line"""
        for l in point.lines:
            if line!=l and l.count_polygons()==1:
                return QtCore.QPointF(
                    (l.p1.x+l.p2.x)/2,(l.p1.y+l.p2.y)/2) 
        return None        

    def del_polygon(self, polygon):
        """Delete polygon"""
        self.polygons.remove(polygon)
        p = copy(self.polygons)
        self.groups = []
        while len(p)>0:
            self.groups.append(p.pop())
            all = False
            # all neighbor is added
            while all:
                all = True
                move = []
                for polygon in p:
                    for line in polygon.lines:                        
                        second = polygon.get_second(line)
                        if second is not None and second in self.groups[-1]:
                            move.append(polygon)
                            all=False
                            break
                for polygon in move:
                    p.remove(polygon)
                    self.groups[-1].append(polygon)
            for i in range(0, len(self.groups)):
                self._make_group_boundary(i) 
                    
    def add_inner_polygon(self, diagram, outside, cluster):
        """Add boundary part polyline"""
        for point in cluster.inner_joins: 
            clusters = [cluster]
            paths = []
            if self._get_fake_path(outside, point, point, paths, clusters):
                revers_points = []
                # make test polygon
                for i in range(0, len(paths), 2):
                    if i==0:
                        test_polyline = self.get_boundary_polyline(paths[i].group_idx, 
                            paths[i].points[0], paths[i].points[-1])
                    else:
                        poly = self.get_boundary_polyline(paths[i].group_idx, 
                            paths[i].points[0], paths[i].points[-1])
                        test_polyline.join(poly)
                    revers_points.append(self._get_test_Point(test_polyline.points[-1], 
                        test_polyline.lines[-1]))
                    poly = outside._make_polyline_from_path(paths[i+1])
                    test_polyline.join(poly)
                test_polygon = QtGui.QPolygonF()        
                for p in test_polyline.points:
                    test_polygon.append(p.qpointf())
                for i in range(0, len(paths), 2):
                    reverse = test_polygon.containsPoint(revers_points[int(i/2)], QtCore.Qt.OddEvenFill)
                    if i==0:
                        polyline = self.get_boundary_polyline(paths[i].group_idx, 
                            paths[i].points[0], paths[i].points[-1], reverse)
                    else:
                        poly = self.get_boundary_polyline(paths[i].group_idx, 
                            paths[i].points[0], paths[i].points[-1], reverse)
                        polyline.join(poly)
                    poly = outside._make_polyline_from_path(paths[i+1])
                    polyline.join(poly)
                polygon = outside.make_polygon_diagram(diagram, polyline)
                for i in range(0, len(paths), 2):                    
                    poly = outside._make_polyline_from_path(paths[i+1])
                    outside.split_bundled_cluster_to_polygon(clusters[int(i/2)+1], polygon)
                    i += 1
                outside.add_cluster_to_polygon(polygon)
                outside.add_bundled_to_polygon(polygon)
                #TODO process inner objects
                return True
        return False

    
class PolylineCluster():
    """
    Cluster of bundled polylines
    """
    def __init__(self, first_line=None, join=None, inner_join=None):
        
        self.polylines = []
        """Bundled polylines"""
        if first_line is not None:
            self.polylines.append(Polyline(first_line))
        self.bundles = []
        """Polyline joins (Points)"""
        self.joins = []        
        """Points, that is line join with shape. (None -> line is not join)"""
        if join is not None:
            self.joins.append(join)
        self.inner_joins = []
        """Points, that is line join with inner shape. (None -> line is not join)"""
        if inner_join is not None:
            self.inner_joins.append(inner_join)
        self.split_polygon = False
        """Some budled cluster have two joins, try split polygon"""
        self.check_inner_polygons = False
        """Inner polygon could be created in polyline in
        cyrcle_poly variable."""
        self.cyrcle_poly = None
        """Polyline that should be get to polygon"""
    
    def get_point(self):
        """Return first found point"""
        return self.polylines[0].points[0]
        
    def set_possition(self, polygon, bundled):
        """All line set in polygon"""
        for poly in self.polylines:
            for line in poly.lines:
                line.in_polygon = polygon
                line.bundled = bundled
        
    def set_bundled(self, bundled):
        """All line set in polygon"""
        for poly in self.polylines:
            for line in poly.lines:
                line.bundled = bundled
        
    def reduce_polylines(self):
        """Return only polylines, that both end points continue"""
        counter = [0]*len(self.bundles)
        bundles = copy(self.bundles)
        for join  in self.joins:
            bundles.append(join)
            counter.append(1)
        for join  in self.inner_joins:
            bundles.append(join)
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
        
    def find_poly_by_end_point(self, point):
        """Find polyline with set end point"""
        for poly in self.polylines:
            if poly.points[-1] == point or \
                poly.points[0] == point:
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
        self.inner = PolygonGroups()
        """Shapes in area"""
        
    def get_container(self, polygon):
        """Get shape that contains polygon"""
        for ipolygon in self.inner.polygons:
            if polygon.spolygon == ipolygon:
                return self
            inner = ipolygon.get_container(polygon)
            if inner is not None:
                return inner
        return None
        
    def is_inner(self):
        """All line have two neighbor polygons"""
        for line in self.boundary_lines:
            if line.polygon2 is None:
                return False
        return True
        
    def get_second(self, line):
        """Return neighbor polygon over set line"""
        if line.polygon1 == None:
            return None
        if line.polygon1.spolygon != self:
            return line.polygon1.spolygon
        if line.polygon2 == None:
            return None
        return line.polygon2.spolygon
    
    def find_cluster(self, line):
        """Return if cluster is bunded and cluster index"""
        for i in range(0, len(self.bundled_clusters)):
            if self.bundled_clusters[i].contains_line(line):
                return True, i
        for i in range(0, len(self.clusters)):
            if self.clusters[i].contains_line(line):
                return False, i
                
    def split_boundary_line(self, line, new_line, new_point):
        """Split line in boundary"""
        p_index = self.boundary_points.index(line.second_point(new_point))
        l_index = self.boundary_lines.index(line)        
        if p_index == l_index:
            self.boundary_lines.insert(l_index+1, new_line)
            self.boundary_points.insert(p_index+1, new_point)
        else:
            self.boundary_lines.insert(l_index, new_line)
            self.boundary_points.insert(p_index, new_point)
        
    def split_line(self, line, new_line, new_point):
        """Split line in polygon"""
        if line.bundled:
            clusters = self.bundled_clusters
        else:
            clusters = self.clusters
            
        for cluster in clusters:
            for poly in cluster.polylines:
                if line in poly.lines: 
                    p_index = poly.points.index(line.second_point(new_point))
                    l_index = poly.lines.index(line)                        
                    if p_index == l_index:
                        poly.lines.insert(l_index+1, new_line)
                        poly.points.insert(p_index+1, new_point)
                    else:
                        poly.lines.insert(l_index, new_line)
                        poly.points.insert(p_index, new_point)
                
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
            appended = self._append_in_polygon(lp, p, line)
            res = False
        else:
            appended = self._append_to_boundary(lp, p, line)
        if appended is None:
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
                cluster1.inner_joins.extend(cluster2.inner_joins)
                cluster1.split_polygon = True
        
    def _join_two_boundary(self, cluster, lp, p, line):
        """Join two boundary clusters"""
        joined = False            
        #try join to boundary
        if lp>2:
            for bp in self.boundary_points:
                if p==bp:
                    cluster.joins.append(p)
                    cluster.split_polygon = True
                    joined = True
                    break   
            if not joined:
                for gbp in self.inner.boundaries_points:
                    for bp in gbp:
                        if p==bp:
                            cluster.inner_joins.append(p)
                            cluster.split_polygon = True
                            joined = True
                            break
                    if joined:
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
                    cluster.joins.append(p)
                    joined = True
                    break
            if not joined:
                for gbp in self.inner.boundaries_points:
                    for bp in gbp:
                        if p==bp:
                            self.clusters.remove(cluster)
                            self.bundled_clusters.append(cluster)
                            cluster.inner_joins.append(p)
                            joined = True
                            break 
                    if joined:
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
                for gbp in self.inner.boundaries_points:
                    for bp in gbp:
                        if p==bp:
                            res_cluster = PolylineCluster(line, None, p)
                            self.bundled_clusters.append(res_cluster)
                            break
                    if res_cluster is not None:
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
        
    def _make_polyline_from_path(self, path):
        """Join path to one polyline"""
        res = Polyline()
        if len(path)==1 or path[0].points[-1]==path[1].points[0] or \
            path[0].points[-1]==path[1].points[-1]:
            res.lines = copy(path[0].lines)
            res.points = copy(path[0].points)
        else:
            res.lines = path[0].lines[::-1]
            res.points = path[0].points[::-1]
        
        for i in range(1, len(path)):
            if res.points[-1]==path[i].points[0]:
                res.lines.extend(path[i].lines)
                res.points.extend(path[i].points[1:])
            else:
                res.lines.extend(path[i].lines[::-1])
                res.points.extend(path[i].points[-2::-1])
        return res
        
    def _find_line_in_polylines(self, polylines, line):
        """Find polyline containing set line in polylines list"""
        for polyline in polylines:
            if line in polyline.lines:
                return polyline
        return None
        
    def _find_line_in_polylines_point(self, polylines, point):
        """Find polyline containing set line in polylines list"""
        for polyline in polylines:
            if point==polyline.points[0] or point==polyline.points[-1]:
                return polyline
        return None  
        
    def _find_path(self, path, polylines, start_point, end_point):
        """Try recursivly find path to set end_point"""
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
                new_polylines = copy(polylines)
                new_path = copy(path)
                new_polylines.remove(poly)
                new_path.append(poly)
                if poly.points[0]==start_point:
                    res = self._find_path(new_path, new_polylines, poly.points[-1], end_point)
                else:
                    res = self._find_path(new_path, new_polylines, poly.points[0], end_point)
                if res is not None:
                    return res
        return None
            
    def add_bundled_to_polygon(self, polygon):
        """Move bundled clusters to set polyline from this
        to set polygon"""
        #TODO process inner objects
        for cluster in self.bundled_clusters:
            if polygon.spolygon.gtpolygon.containsPoint(cluster.get_point().qpointf(), QtCore.Qt.OddEvenFill):                
                self.bundled_clusters.remove(cluster)
                polygon.spolygon.bundled_clusters.append(cluster)
                cluster.set_possition(polygon.spolygon, True)        
        
    def split_bundled_cluster_to_polygon(self, cluster, polygon):
        """Move bundled clusters split set polyline from this
        to set polygon"""
        #TODO process inner objects
        joins = []        
        for bundle in cluster.bundles:
            if bundle in polygon.spolygon.boundary_points:
                joins.append(bundle)
        for join in joins:
            cluster.bundles.remove(join)
        remove = []
        moved = {}
        for poly in cluster.polylines:
            if poly.lines[0] in polygon.spolygon.boundary_lines:
                remove.append(poly)
                continue
            index = None            
            if poly.points[0] in joins:
               index = joins.index(poly.points[0])
               second = poly.points[-1]
            if poly.points[-1] in joins:
               index = joins.index(poly.points[-1])
               second = poly.points[0]
            if index is not None:
                if polygon.spolygon.gtpolygon.containsPoint(second.qpointf(), QtCore.Qt.OddEvenFill):
                    polygon.spolygon.bundled_clusters.append(PolylineCluster(None, joins[index]))
                    polygon.spolygon.bundled_clusters[-1].polylines.append(poly)
                    if second in cluster.bundles:
                        moved[second] = polygon.spolygon.bundled_clusters[-1]
                        cluster.bundles.remove(second)
                        polygon.spolygon.bundled_clusters[-1].bundles.append(second)
                else:
                    self.bundled_clusters.append(PolylineCluster(None, None, joins[index]))
                    self.bundled_clusters[-1].polylines.append(poly)
                    if second in cluster.bundles:
                        moved[second] = self.bundled_clusters[-1]
                        cluster.bundles.remove(second)
                        self.bundled_clusters[-1].bundles.append(second)
                del joins[index]            
                remove.append(poly)
        for poly in remove:
            cluster.polylines.remove(poly)
        while len(cluster.polylines)>0:
            remove = []
            for poly in cluster.polylines:
                if poly.points[0] in moved:
                    remove.append(poly)                        
                    moved[poly.lines[0]].polylines.append(poly)
                    second = poly.points[-1]
                    if second in cluster.bundles:
                        moved[second] = moved[poly.lines[0]]
                        cluster.bundles.remove(second)
                        moved[poly.lines[0]].bundles.append(second)
                elif poly.points[-1] in moved:
                    remove.append(poly)                        
                    moved[poly.lines[-1]].polylines.append(poly)
                    second = poly.points[-1]
                    if second in cluster.bundles:
                        moved[second] = moved[poly.lines[-1]]
                        cluster.bundles.remove(second)
                        moved[poly.lines[-1]].bundles.append(second)
            for poly in remove:
                cluster.polylines.remove(poly)                    
        self.bundled_clusters.remove(cluster)
        for cluster in polygon.spolygon.bundled_clusters:
            cluster.set_possition(polygon.spolygon, True)
        
        
    def add_cluster_to_polygon(self, polygon):
        """Split free clusters to set polygon and this"""
        for cluster in self.clusters:
            if polygon.spolygon.gtpolygon.containsPoint(cluster.get_point().qpointf(), QtCore.Qt.OddEvenFill):
                self.clusters.remove(cluster)
                polygon.spolygon.clusters.append(cluster)
                cluster.set_possition(polygon)

    def apply_add_line_changes(self, diagram, polygon, line):    
        """apply all changes after one operation"""
        for cluster in self.clusters:
            if cluster.check_inner_polygons:
                if cluster.cyrcle_poly is not None:
                    self.make_polygon_from_cyrcle(diagram, cluster, cluster.cyrcle_poly)
                    cluster.cyrcle_poly = None
                else:
                    polylines = cluster.reduce_polylines()
                    start_polyline = self._find_line_in_polylines(polylines, line)
                    path = self._find_path([start_polyline], polylines, 
                        start_polyline.points[0], start_polyline.points[-1])
                    if len(path)>0:
                        polyline = self._make_polyline_from_path(path) 
                        self.make_polygon_from_cyrcle(diagram, cluster, polyline)
                        return True
                cluster.check_inner_polygons = False
                return True
        for cluster in self.bundled_clusters:
            if cluster.split_polygon:
                if len(cluster.inner_joins)>1:
                    if self.inner.add_inner_polygon(diagram, self, cluster):
                        cluster.split_polygon = False                        
                        return True
                
    def make_polygon_diagram(self, diagram, polyline):
        """Make diagram polygon object"""
        polygon = diagram.add_polygon(polyline.lines)
        polygon.spolygon = SimplePolygon()
        polygon.spolygon.boundary_lines = polyline.lines
        polygon.spolygon.boundary_points = polyline.points[0:-1]        
        self.inner.add_polygon(polygon.spolygon)
        polygon.spolygon.reload_shape_boundary(polygon, True)
        return polygon

    def make_polygon_from_cyrcle(self, diagram, cluster, polyline):
        """Make polygon from path"""
        p = polyline.points[0]
        polygon = self.make_polygon_diagram(diagram, polyline)
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
        self.add_bundled_to_polygon(polygon)
        self.add_cluster_to_polygon(polygon)


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

   
class SimplePolygon(Shape):
    """
    Polygon without bundled polyline
    """
    
    def __init__(self):
        super(SimplePolygon, self).__init__()
        self.gtpolygon = None
        """Qt polygon"""
        
    def get_boundary_polyline(self, p1, p2, reverse=False):
        """Get boundary polyline from point p1 to p2"""
        return Polyline.get_boundary_polyline(self.boundary_lines, self.boundary_points, p1, p2, reverse)

    def disjoin(self, line):
        """disjoin shape"""
        pass
    
    def take(self, line):
        """take away line from shape"""
        pass
    
    def remove(self, line):
        """remove line from shape"""
        pass
        
    def join_inner_shape(self, diagram, polygon):
        """Try join boundary with inner shape"""
        # TODO: inner polygon join with outer by line
        return False
        
    def _split_polygon_by_path(self, diagram, polygon, cluster, path):
        """Split poligon to two according to path"""        
        polyline = self._make_polyline_from_path(path)         
        boundary1 = self.get_boundary_polyline(polyline.points[0], polyline.points[-1])
        boundary2 = self.get_boundary_polyline(polyline.points[-1], polyline.points[0])        
        
        for line in polyline.lines:
            line.polygon1 = polygon
            line.polygon2 = None
        for line in boundary2.lines:
            if line.polygon1 == polygon:
                line.polygon1 = line.polygon2
            line.polygon2 = None
            
        boundary1.join(polyline)
        boundary2.join(polyline)
        new_polygon = self.make_polygon_diagram(diagram, boundary2)
        
        self.gtpolygon = QtGui.QPolygonF()
        for p in boundary1.points:
            self.gtpolygon.append(p.qpointf())
        self.boundary_lines = boundary1.lines
        self.boundary_points = boundary1.points[0:-1]
        
        self.split_bundled_cluster_to_polygon(cluster, new_polygon)
        self.add_cluster_to_polygon(new_polygon)
        self.add_bundled_to_polygon(new_polygon)
        #TODO process inner objects
        
        self.reload_shape_boundary(polygon, False)
        parent = PolygonOperation.get_container(diagram, polygon)        
        parent.inner.add_polygon(new_polygon.spolygon)
        
    def split_shape(self, diagram, polygon, cluster):
        """Try join boundary with inner shape"""
        if cluster.joins[0] == cluster.joins[1]:
            # TODO: inner polygon with one point
            pass
        else:
            polylines = cluster.reduce_polylines()
            for poly in polylines:
                if poly.points[0]==cluster.joins[0] or \
                    poly.points[-1]==cluster.joins[0]:
                    if (poly.points[0]==cluster.joins[0] and \
                        poly.points[-1]==cluster.joins[1]) or \
                        (poly.points[-1]==cluster.joins[0] and \
                        poly.points[0]==cluster.joins[1]):
                        self._split_polygon_by_path(diagram, polygon, cluster, [poly])
                        return True
                    new_polylines = copy(polylines)
                    new_polylines.remove(poly)
                    if poly.points[0]==cluster.joins[0]:
                        path = self._find_path([poly], new_polylines, poly.points[-1], 
                            cluster.joins[1])
                    else:
                        path = self._find_path([poly], new_polylines, poly.points[0], 
                            cluster.joins[1])
                    if len(path)>0:
                        self.split_polygon_by_path(diagram, polygon, cluster, path)
                        return True
        return False
        
    def reload_shape_boundary(self, polygon, only_possition):
        """Try add or remove bundled structures to boundary. If not
        count of boundary points changed, reload only shape contour"""
        if not only_possition:
            polygon.lines = []
            for line in self.boundary_lines:
                polygon.lines.append(line)                
        polygon.spolygon.gtpolygon = QtGui.QPolygonF()        
        for p in self.boundary_points:
            polygon.spolygon.gtpolygon.append(p.qpointf())
        polygon.spolygon.gtpolygon.append(self.boundary_points[0].qpointf())
        if polygon.object is not None:
            polygon.object.refresh_polygon()
        return False
        
    def apply_add_line_changes(self, diagram, polygon, line):    
        """apply all changes after one operation"""
        if super(SimplePolygon, self).apply_add_line_changes(diagram, polygon, line):
            return True
        for cluster in self.bundled_clusters:
            if cluster.split_polygon:
                if len(cluster.inner_joins)>0 and len(cluster.joins)>0:
                    if self.join_inner_shape(diagram, polygon, cluster):
                        cluster.split_polygon = False                        
                        return True
                if len(cluster.joins)>1:
                    if self.split_shape(diagram, polygon, cluster):
                        cluster.split_polygon = False                        
                        return True


class PolygonOperation():
    """
    Static class for polygon localization
    """
    line_spliting = None
    """Note about spliting line in next add operation"""
    
    @classmethod    
    def next_split_line(cls, line):
        """Set note about spliting line in next add operation"""
        cls.line_spliting = line
    
    @staticmethod
    def get_container(diagram, polygon):
        """Get shape that contains polygon"""
        return diagram.outside.get_container(polygon) 
    
    @staticmethod
    def find_polygon(diagram, point):
        """Try find polygon that contains point"""
        for polygon in diagram.polygons:
            if polygon.spolygon.gtpolygon.containsPoint(point, QtCore.Qt.OddEvenFill):
                return polygon
        return None
        
    @staticmethod
    def _find_polygon_from_spolygon(diagram, spolygon):
        """Try find polygon from spolygon"""
        for polygon in diagram.polygons:
            if spolygon==polygon.spolygon:
                return polygon
        
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
                    else:
                        if l.polygon2 is not None:
                            if l.polygon2.spolygon.gtpolygon.containsPoint(p2, QtCore.Qt.OddEvenFill):
                                return l.polygon2 
                        parent = PolygonOperation.get_container(diagram, l.polygon1)
                        if parent == diagram.outside:
                            return None
                        else:
                            return cls._find_polygon_from_spolygon(diagram, parent)
        return None
    
    @classmethod
    def split_line(cls, diagram, line, new_line):
        """Find and split line by new point"""
        if line.p1 == new_line.p1 or line.p1 == new_line.p2:
            new_point = line.p1
        else:
            new_point = line.p2
            
        new_line.bundled = line.bundled
        new_line.in_polygon = line.in_polygon
        new_line.polygon1 = line.polygon1
        new_line.polygon2 = line.polygon2
        
        if line.in_polygon is not None:
            line.in_polygon.spolygon.split_line(line, new_line, new_point)
        elif line.polygon1 is not None:
            line.polygon1.spolygon.split_boundary_line(line, new_line, new_point)
            line.polygon1.spolygon.reload_shape_boundary(line.polygon1, False)
            if line.polygon2 is not None:
                line.polygon2.spolygon.split_boundary_line(line, new_line, new_point)
                line.polygon2.spolygon.reload_shape_boundary(line.polygon2, False)            
            parent = PolygonOperation.get_container(diagram, line.polygon1)        
            parent.inner.refresh_polygon(line.polygon1.spolygon)    
        else:
            diagram.outside.split_line(line, new_line, new_point)
        
        
    @classmethod
    def find_polygon_boundary(cls, line):
        """Try find polygon that contains line"""
        return None
    
    @classmethod
    def update_polygon_add_line(cls, diagram, line):
        """Update polygon structures after add line"""
        if cls.line_spliting is not None:
            line2 = cls.line_spliting
            cls.line_spliting = None
            cls.split_line(diagram, line2, line)
            return
        bundled = False
        lp1 = len(line.p1.lines)
        lp2 = len(line.p2.lines)
        if lp1>1 and lp2>1:
            middle = QtCore.QPointF(
                (line.p1.x+line.p2.x)/2,(line.p1.y+line.p2.y)/2)                
            polygon = cls.find_polygon_by_neighbors(diagram, line, line.p1, middle)
            if polygon is None:
                bundled = diagram.outside.join(line)                
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
                bundled = diagram.outside.append(line)
            else:
                bundled = polygon.spolygon.append(line)
        else:
            p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(diagram, p)
            if polygon is None:
                bundled = diagram.outside.add(line)                
            else:
                bundled = polygon.spolygon.add(line)
        line.bundled = bundled
        if polygon is None:
            diagram.outside.apply_add_line_changes(diagram, None, line)
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
                diagram.outside.disjoin(line)
            else:
                polygon.disjoin(line)
        elif lp1>1 or lp2>1:
            if lp1>1:
                p = QtCore.QPointF( line.p2.x, line.p2.y)
            else:
                p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                diagram.outside.take(line)
            else:
                polygon.take(line)
        else:
            p = QtCore.QPointF( line.p1.x, line.p1.y)
            polygon = cls.find_polygon(p)
            if polygon is None:
                diagram.outside.remove(line)
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
