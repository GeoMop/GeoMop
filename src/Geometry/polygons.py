import numpy as np
import bisect
import numpy.linalg as la
import enum

# TODO: rename point - > node

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
        self.wires = IdMap()
        # Closed loops possibly degenerated) of segment sides. Single wire can be tracked through segment.next links.
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
            wire = segment.wire[i_side]
            return (False, wire)

    def _snap_to_polygon(self, polygon, point):
        for pt in polygon.free_points:
            if la.norm(point - pt.xy) < self.tolerance * pt.magnitude:
                return (0, pt, polygon)
        return (2, polygon, None)

    def snap_point(self, point):
        """
        Find object (point, segment, polygon) within tolerance from given point.
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
            wire0 = t0

        px, seg1 = edges_on_y_axes[i+1]
        is_snapped, t1 =  self._snap_to_segment(seg1, point, up_is_cc=True)
        if is_snapped:
            return (1, seg1, t1)
        else:
            wire1 = t1

        assert wire0.polygon == wire1.polygon
        return self._snap_to_polygon(wire0.polygon, point)


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
            (t0, t1) = e.intersection(a, b)
            if t1 is not None:
                mid_pt = self._split_segment(e, t0)
                t_list.append( (t1, e, mid_pt) )
        t_list.sort()
        start_pt = a_point
        for t, e, mid_pt in t_list:
            self._new_segment(start_pt, mid_pt)
            start_pt = mid_pt
        self._new_segment(start_pt, b_point)

    def move_points(self):
        pass



    # Helper change operations.
    def _append_segment(self, seg):
        self.segments.append(seg)
        self.points_to_segment[ seg.vtxs_ids() ] = seg

    def _remove_segment(self, seg):
        del self.points_to_segment[ seg.vtxs_ids() ]
        del self.segments[seg.id]

    def _point_join_segment(self, point, seg):
        if point.segment == None:
            point.poly = None
            point.segment = seg

    def _point_rm_segment(self, point, seg):
        if point.segment == seg:
            for new_seg in self.point_segments(point):
                if not new_seg == seg:
                    point.segment = new_seg
                    return
            assert seg.is_dendrite()
            point.poly = seg.wire[0].polygon
            point.segment = None


    # Special getters.
    def point_segments(self, point, start_segment=None ):
        """
        Generator for segments joined to the point.
        yields: (segment, vtx_idx), where vtx_idx is index of 'point' in 'segment'
        """
        if start_segment is None:
            start_segment = point.segment
        if start_segment is None:
            return
        seg = start_segment
        while (1):
            yield seg
            outgoing = ( point == seg.vtxs[0] )
            next_side = right_side if outgoing else left_side
            seg = seg.next[next_side]
            if seg == start_segment:
                return

    def segment_previous(self, seg, side):
        """
        Oposite of seg.next[side]. Implemented through loop around a node.
        :param seg:
        :param side:
        :return:
        """
        vtx = 0 if side == left_side else 1
        for s in self.point_segments(seg.points[vtx], seg):
            pass
        return s

    def point_insert_segment(self, point, vector):
        vec_angle =  np.angle(complex(vector[0], vector[1]))
        for seg in self.point_segments(point):
            seg_vec = seg.vector()
            if not point.is_outgoing(seg):
                seg_vec *= -1.0
            angle = np.angle(complex(seg_vec[0], seg_vec[1]))
            da = angle - vec_angle
            if da < 0.0:
                da += 2*np.pi
            if da > last[1]:
                return (last[0], seg)
            last = (seg, da)



    # Reversible atomic change operations.
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
        poly.free_points[point.id] = pt
        return pt


    def _remove_free_point(self, point):
        assert point.poly is not None
        assert point.segment is None
        del point.poly.free_points[point.id]
        del self.points[point.id]


    def _split_segment(self, seg, t_point):
        """
        Split a segment into two segments. Original keeps the start point.
        :param seg:
        :param t_point:
        :return:
        """
        self._point_rm_segment(seg.vtxs[1], seg)

        xy_point = seg.paramteric(t_point)
        mid_pt = Point(xy_point, None)
        self.points.append(mid_pt)

        prev_seg = self.segment_previous(seg, right_side)
        prev_side = right_side if seg.points[1].is_outgoing(prev_seg) else left_side
        new_next = [None, None]
        new_next[left_side] = seg.next[left_side]
        new_next[right_side] = seg
        new_seg = Segment((mid_pt, seg.vtxs[1]), seg.wire, new_next)
        seg.vtxs[1] = mid_pt
        seg.next[left_side] = new_seg
        prev_seg.next[prev_side] = new_seg

        self._point_join_segment(mid_pt, new_seg)
        self._append_segment(new_seg)
        return mid_pt


    def _join_segments(self, mid_point, seg0, seg1):
        assert mid_point.segment == seg0 or mid_point.segment == seg1
        # TODO: implement segment inversion and allow joining of any two segments
        assert seg0.point[1] == mid_point
        assert seg1.point[0] == mid_point

        # Assert that no other segments are joined to the mid_point
        assert seg0.next[left_side] == seg1
        assert seg1.next[right_side] == seg0

        prev_seg = self.segment_previous(seg1, right_side)
        prev_side = right_side if seg1.points[1].is_outgoing(prev_seg) else left_side
        seg0.vtxs[1] = seg1.vtxs[1]
        seg0.next[left_side] = seg1.next[left_side]
        prev_seg[prev_side] = seg0

        # fix possible polygon references
        for side in [left_side, right_side]:
            wire = seg1.wire[side]
            if wire.segment == seg1:
                wire.segment = seg0

        self._remove_segment(seg1)
        del self.points[mid_point.id]


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

        vec = b_pt.xy - a_pt.xy
        left_prev, right_next = self.point_insert_segment(a_pt, vec)
        right_prev, left_next = self.point_insert_segment(b_pt, -vec)
        left_prev_side  = right_side if a_pt.is_outgoing(left_prev) else left_side
        right_prev_side = right_side if b_pt.is_outgoing(right_prev) else left_side
        next  = [None, None]
        next[left_side] = left_next
        next[right_side] = right_next
        # TODO: split polygon
        # - need to separate boundary components
        # - replace polygons by wires; segments points to wires a "side of a boundary"
        # - polygon will beformed by outer wire and holes
        # - Wires refers to its polygon
        # - after connection we either connect two wires into one or split one wire into two
        # - then we must decide if one wire is inside other wire or ther are disjoint

        left_poly = left_prev.wire[left_prev_side]
        right_poly = right_prev.wire[right_prev_side]



        new_seg = Segment([a_pt, b_pt], new_polygons, next)
        self._append_segment(new_seg)
        left_prev.next[left_prev_side] = new_seg
        right_prev.next[right_prev_side] = new_seg


    def _del_segment(self, segment_id):
        pass


# Data classes contins no modification methods, all modifications are through reversible atomic operations.
class Point:
    def __init__(self, id, point, poly):
        self.id = id
        self.xy = point
        self.poly = poly
        # Containing polygon for free-nodes. None for others.
        self.segment = None
        # One of joined segments for non-free nodes. None for the free ones.

    def __eq__(self, other):
        return self.id == other.id

    def is_outgoing(self, segment):
        return self == segment.points[0]

class Segment:
    def __init__(self, id, vtxs, wire, next):
        self.id = id
        self.vtxs = vtxs
        # tuple (start, end) point object
        self.wire = wire
        # (left_poly, right_poly) - polygons on left and right side
        #self.ori = ori
        # (left_ori, right_ori); indicator if segment orientation match ccwise direction of the polygon
        #self.prev = prev
        # (left_prev, right_prev);  previous edge for left and right side;
        self.next = next
        # (left_next, right_next); next edge for left and right side;

    def contains_point(self, pt):
        Dxy = self.vector()
        axis = np.argmax(Dxy)
        D = Dxy[axis]
        magnitude = max([self.vtxs[0].xy[axis], self.vtxs[1].xy[axis] ])
        assert np.abs(D) > 1e-12 * magnitude
        t = (pt[axis] - self.vtxs[0].xy[axis]) / D
        if 0 <= t <= 1:
            return t
        else:
            return None

    def intersection(self, a, b):
        """
        Find intersection of 'self' and (a,b) edges.
        :param a: start vtx of edge1
        :param b: end vtx of edge1
        :return: (t0, t1) Parameters of the intersection for 'sef' and other edge.
        """
        mat = np.array([ self.vector(), a - b])
        rhs = a - self.vtxs[0].xy
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

    def __eq__(self, other):
        return self.id == other.id

    def is_dendrite(self):
        return self.wire[left_side] == self.wire[right_side]

    def vector(self):
        return (self.vtxs[1].xy - self.vtxs[0].xy)

    def parametric(self, t):
        return  self.vector() * t + self.vtxs[0].xy


class Wire:
    def __init__(self):
        self.parent = None
        # Wire that contains this wire. None for the global outer boundary.
        # Parent relations are independent of polygons.
        self.polygon = None
        # Polygon of this wire
        self.segment
        # One segment of the wire.

    def __eq__(self, other):
        return self.id == other.id


    def get_outer_segments(self):
        """
        :return: List of boundary componencts without tails. Single component is list of segments (with orientation)
        that forms outer boundary, i.e. excluding internal tails, i.e. segments appearing just once.
        """
        component = []
        segment = self.segment
        while (1):
            side = left_side if self.segment.wire[left_side] == self else right_side
            if not segment.is_dendrite():
                component.append( (segment, side) )
            segment = segment.next[side]
            if segment == self.segment:
                break
        return component


class Polygon:
    def __init__(self, wires):
        self.wires = wires
        # First is outer wire, next are hole wires.
        self.free_points = {}
        # Dict ID->pt of free points inside the polygon.


    def __eq__(self, other):
        return self.id == other.id


