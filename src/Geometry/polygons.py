import numpy as np
import bisect
import numpy.linalg as la
import enum


left_side = 0
right_side = 1


class IdMap(dict):
    id = 0

    def append(self, obj):
        obj.id = self.id
        self[id] = obj
        self.id += 1


class PolygonDecomposition:
    """
    Decomposition of a plane into (non-convex) polygonal subsets (not necessarily domains).
    """

    def __init__(self):
        """
        Constructor.
        """
        self.points = IdMap()
        # Points dictionary ID -> Point
        self.segments = IdMap()
        # Segmants dictionary ID - > Segmant
        self.pt_to_seg = {}
        # dict (a.id, b.id) -> segment
        self.polygons = IdMap()
        # Polygon dictionary ID -> Polygon
        self.polygons.append(Polygon(0, None))

        #
        self.tolerance = 0.01

        events = []
        # Primitive list of (macro) events,
        i_active_event = 0
        # Position to write to next new event.


    def set_tolerance(self, tolerance):
        """
        Set tolerance for snapping to existing points and lines.
        Should be given by actual zoom level.
        :param tolerance: float, a distance used to snap points to existing objects.
        :return: None
        """
        self.tolerance = tolerance

    # History operations
    #
    # def undo(self, n_steps):
    #     self.i_active_event -= 1
    #     for
    #
    # def redo(self, n_steps):
    #     self.i_active_event += 1
    #
    #
    # def add_events(self, event_bundle):
    #     assert event_bundle is list
    #     self.events = self.events[0:self.i_active_event]
    #     self.events.append(event_bundle)


    def _snap_to_segment(self, segment, point, up_is_cc ):
        tt = segment.contains_point(point)
        if tt is not None:
            return (True, tt)
        else:
            up_ori = segment.points[1, 1] > segment.points[0, 1]
            i_side = int(up_ori == up_is_cc)    # Left - 0, Right - 1
            poly = segment.polygon[i_side]
            return (False, poly)

    def _snap_to_polygon(self, polygon, point):
        for pt in polygon.free_points:
            if la.norm(point - pt.point) < self.tolerance * pt.magnitude:
                return (0, pt, polygon)
        return (2, polygon, None)

    def snap_point(self, point):
        """
        Find object (point, segment, polygon) within tolerance form given point.
        :param point: numpy array X, Y
        :return: (dim, obj, param) Where dim is object dimension (0, 1, 2), obj is the object (Point, Segment, Polygon).
        'param' is:
          Point: polygon containing the free point
          Segment: parameter 't' of snapped point on the segment
          Polygon: None
        """
        #pt = np.array(point, dtype=float)
        x_pt, y_pt = point
        edges_on_y_axes = []
        for e in self.segments:
            vtxs = np.array([ e.vtxs[0].xy, e.vtxs[1].xy])
            Dy = vtxs[1, 1] - vtxs[0, 1]
            magnitude = np.max(vtxs[:, 1])
            # require at least 4 decimal digit remaining precision of the Dy
            if np.abs(Dy) < 1e-12 * magnitude:
                # horizontal edge
                if vtxs[1, 0] <= y_pt <= vtxs[0, 1]:
                    edges_on_y_axes.append( (vtxs[0, 0], e) )
                    edges_on_y_axes.append( (vtxs[0, 1], e) )
            else:
                t = ( y_pt - vtxs[0, 1]) / Dy
                if 0 <= t <= 1:
                    Dx = vtxs[1, 0] - vtxs[0, 0]
                    isec_x = t * Dx + vtxs[0, 0]

                    edges_on_y_axes.append( (isec_x, e) )
        edges_on_y_axes.sort()
        i = bisect.bisect_left(edges_on_y_axes, x_pt)
        # i ... minimal i for which edges_on_y_axes[i] <= x_pt
        #  both e[i] and e[i+1] are from vertical lines
        #  one or both of e[i] and e[i+1] are from horizontal lines
        #  We check all these edges for incidence with Point.
        px, seg0 = edges_on_y_axes[i]
        is_snapped, t0 =  self._snap_to_segment(seg0, point, up_is_cc=False)
        if is_snapped:
            if t0 <= 0 + self.tolerance:
                return (0, seg0.vtxs[0], seg0)
            if t0 >= 1 - self.tolerance:
                return (0, seg0.vtxs[1], seg0)
            return (1, seg0, t0)
        else:
            poly0 = t0

        px, seg1 = edges_on_y_axes[i+1]
        is_snapped, t1 =  self._snap_to_segment(seg1, point, up_is_cc=True)
        if is_snapped:
            return (1, seg1, t1)
        else:
            poly1 = t1

        assert poly0 == poly1
        return self._snap_to_polygon(poly0, point)


    # Macro operations.
    def add_point(self, point):
        """
        Try to add a new point, checking snapping to lines and existing points.
        :param point: numpy array with XY coordinates
        :param poly: Optional polygon that should contain the point
        :return: Point instance.

        This operation translates to add_free_point or to split_line_by_point.
        """
        dim, obj, t = self.snap_point(point)
        if dim == 0:
            # nothing to add
            return obj
        elif dim == 1:
            return self._split_segment(obj, t)
        else:
            poly = t
            return self._add_free_point(obj, point, poly)


    def add_line(self, a, b):
        """
        Try to add new line from point A to point B. Check intersection with any other line and
        call add_point for endpoints and intersections, then call operation connect_points for individual
        segments.
        :param a: numpy array X, Y
        :param b: numpy array X, Y
        :return:
        """
        a_point = self.add_point(a)
        b_point = self.add_point(b)

        t_list = []
        for e in self.edges:
            (t0, t1) = e.line_line(a, b)
            if t1 is not None:
                mid_pt = self._split_segment(e, t0)
                t_list.append( (t1, e, mid_pt) )
        t_list.sort()
        start_pt = a_point
        for t, e, mid_pt in t_list:
            self._new_segment(start_pt, mid_pt)
            start_pt = end_pt
        self._new_segment(start_pt, b_point)

    def move_points(self):
        pass

    def _append_segment(self, seg):
        self.segments.append(seg)
        self.points_to_segment[ seg.vtxs_ids() ] = seg

    def _remove_segment(self, seg):
        del self.points_to_segment[ seg.vtxs_ids() ]
        del self.segments[seg.id]


    # Reversible operations
    # Action ( forward, backward ),
    # forward = (add_free_point, X, Y)  ... func name, params
    # backward = (remove_free_point, pt_id) ... func name , params
    def _add_free_point(self, point, poly):
        """
        :param point: XY array
        :return: Point instance
        """

        pt = Point(point, poly)
        self.points.append(pt)
        return pt


    def _remove_free_point(self, point):
        pass

    def _split_segment(self, seg, point):
        """
        Split a segment into two segments. Original keeps the start point.
        :param seg:
        :param t_point:
        :return:
        """
        mid_pt = Point(point, None)
        self.points.append(mid_pt)

        new_seg = Segment((mid_pt, seg.vtxs[1]), seg.polygon, seg.ori, (seg, seg), seg.next)
        seg.vtxs[1] = mid_pt
        seg.next = (new_seg, new_seg)

        # mid_pt.segments.append(new_seg)
        # mid_pt.segments.append(seg)
        #
        # del new_seg.vtx[1].segments[seg.id]
        # new_seg.vtx[1].segments[new_seg.id] = new_seg

        self._append_segment(new_seg)
        return mid_pt


    def _join_lines(self, point, lines):
        pass

    def _new_segment(self, a_pt, b_pt):
        """
        Add segment between given existing points. Assumes that there is no intersection with other segment.
        Just return the segment if it exists.
        :param a_pt: Start point of the segment.
        :param b_pt: End point.
        :return: new segment
        """
        segment = self.points_to_segment.get((a_pt.id, b_pt.id), None)
        if segment is not None:
            return segment





    def _del_segment(self, segment_id):
        pass


# Data classes contins no modification methods, all modifications are through reversible atomic operations.
class Point:
    def __init__(self, id, point, poly):
        self.id = id
        self.pt = point
        self.poly = poly
        # self.segments = []


class Segment:
    def __init__(self, id, vtxs, polygon, ori, prev, next):
        self.id = id
        self.vtxs = vtxs
        # tuple (start, end) point object
        self.polygon = polygon
        # (left_poly, right_poly) - polygons on left and right side
        #self.ori = ori
        # (left_ori, right_ori); indicator if segment orientation match ccwise direction of the polygon
        #self.prev = prev
        # (left_prev, right_prev);  previous edge for left and right side;
        self.next = next
        # (left_next, right_next); next edge for left and right side;

    def contains_point(self, pt):
        Dxy = self.vtxs[1].point - self.vtxs[0].point
        axis = np.argmax(Dxy)
        D = Dxy[axis]
        magnitude = max([self.vtxs[0].point[axis], self.vtxs[1].point[axis] ])
        assert np.abs(D) > 1e-12 * magnitude
        t = (pt[axis] - self.vtxs[0].point[axis]) / D
        if 0 <= t <= 1:
            return t
        else:
            return None

    def line_line(self, a, b):
        """
        Find intersection of 'self' and (a,b) edges.
        :param a: start vtx of edge1
        :param b: end vtx of edge1
        :return: (t0, t1) Parameters of the intersection for 'sef' and other edge.
        """
        mat = np.array([ self.vtxs[1].point - self.vtxs[0].point, a - b])
        rhs = a - self.vtxs[0].point
        try:
            t0, t1 = la.solve(mat.T, rhs)
        except la.LinAlgError:
            return (None, None)
            # TODO: possibly treat case of overlapping segments
        if 0 <= t0 <=1 and 0 <= t1 <=1:
            return (t0, t1)
        else:
            return (None, None)

    # def is_vertex(self, point):
    #     if point == self.points[0]:
    #          return 0
    #     if point == self.points[1]:
    #         return 1
    #     return None

    def vtxs_ids(self):
        return (self.points[0].id, self.points[1].id)


class Polygon:
    def __init__(self, id, segment):
        self.id = id
        self.segments = [ segment ]
        # First segments of boundary components. With orientation.
        # Indicate if the orientation of the first segment math ccwise direction.

    def __eq__(self, other):
        return self.id == other.id

    def get_outer_segments(self):
        """
        :return: List of boundary componencts without tails. Single component is list of segments (with orientation)
        that forms outer boundary, i.e. excluding internal tails, i.e. segments appearing just once.
        """
        components = []
        for first in self.segments:
            component = []
            segment = first
            while (1):
                side = left_side if first.polygon[left_side] == self else right_side

                if not segment.polygon[left_side] == segment.polygon[right_side]:
                    component.append( (segment, side) )
                segment = segment.next[side]
                if segment == first:
                    break
            components.append(component)
