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
        obj.id = IdMap.id
        IdMap.id += 1
        self[obj.id] = obj


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
        self.outer_polygon = Polygon(None)
        self.polygons.append(self.outer_polygon)
        # add outer polygon


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
        for pt in polygon.free_points.values():
            if la.norm(point - pt.xy) < self.tolerance * pt.magnitude():
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
        point = np.array(point)
        x_pt, y_pt = point
        x_axis_segs = []
        for e in self.segments.values():
            x_isec = e.x_line_isec(point)
            for x_pt in x_isec:
                x_axis_segs.append((x_pt, e))

        if len(x_axis_segs) == 0:
            return self._snap_to_polygon(self.outer_polygon, point)
        x_axis_segs.sort()
        i = bisect.bisect_left(x_axis_segs, (x_pt, e))
        # i ... minimal i for which x_axis_segs[i] <= x_pt
        #  both e[i] and e[i+1] are from vertical lines
        #  one or both of e[i] and e[i+1] are from horizontal lines
        #  We check all these edges for incidence with Point.

        assert i < len(x_axis_segs)
        px, seg0 = x_axis_segs[i]
        is_snapped, t0 =  self._snap_to_segment(seg0, point, up_is_cc=False)
        if is_snapped:
            if t0 <= 0 + self.tolerance:
                return (0, seg0.vtxs[0], seg0)
            if t0 >= 1 - self.tolerance:
                return (0, seg0.vtxs[1], seg0)
            return (1, seg0, t0)
        else:
            wire0 = t0

        if i >= len(x_axis_segs):
            return self._snap_to_polygon(wire0.polygon, point)

        px, seg1 = x_axis_segs[i+1]
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
            poly = obj
            return self._add_free_point(point, poly)


    def add_line(self, a, b):
        """
        Try to add new line from point A to point B. Check intersection with any other line and
        call add_point for endpoints and intersections, then call operation connect_points for individual
        segments.
        :param a: numpy array X, Y
        :param b: numpy array X, Y
        :return:
        """
        a = np.array(a)
        b = np.array(b)
        a_point = self.add_point(a)
        b_point = self.add_point(b)


        seg_list = []
        for e in self.segments.values():
            (t0, t1) = e.intersection(a, b)
            if t1 is not None:
                seg_list.append((e, t0, t1))
        t_list = []
        for seg, t0, t1 in seg_list:
            mid_pt = self._split_segment(e, t0)
            t_list.append( (t1, e, mid_pt) )
        t_list.sort()
        start_pt = a_point
        result = []
        for t, e, mid_pt in t_list:
            result.append( self.new_segment(start_pt, mid_pt) )
            start_pt = mid_pt
        result.append( self.new_segment(start_pt, b_point) )
        return result

    def move_points(self):
        pass


    def new_segment(self, a_pt, b_pt):
        """
        Add segment between given existing points. Assumes that there is no intersection with other segment.
        Just return the segment if it exists.
        :param a_pt: Start point of the segment.
        :param b_pt: End point.
        :return: new segment
        """
        segment = self.pt_to_seg.get((a_pt.id, b_pt.id), None)
        if segment is not None:
            return segment

        if a_pt.is_free() and b_pt.is_free():
            assert a_pt.poly == b_pt.poly
            return self._new_wire(a_pt.poly, a_pt, b_pt)

        vec = b_pt.xy - a_pt.xy
        a_insert = a_pt.insert_segment(vec)
        b_insert = b_pt.insert_segment(-vec)

        if a_pt.is_free():
            assert b_insert[0]
            return self._wire_add_dendrite(b_pt, b_insert, a_pt)
        if b_pt.is_free():
            assert a_insert[0]
            return self._wire_add_dendrite(a_pt, a_insert, b_pt)

        a_prev, a_next, a_side, a_wire = a_insert
        b_prev, b_next, b_side, b_wire = b_insert
        assert a_prev is not None
        assert b_prev is not None

        if a_wire != b_wire:
            return self._join_wires(a_pt, b_pt, a_insert, b_insert)
        else:
            return self._split_poly(a_pt, b_pt, a_insert, b_insert)


    def del_segment(self, segment):
        a_pt, b_pt = segment.points
        # single seg ment vertices
        if segment.next[left_side] == segment and segment.next[right_side] == segment:
            return self._rm_wire_in_poly(segment)
        # one singel segment
        if segment.next[left_side] == segment:
            end_vtx = 1
            return self.rm_dendrite(segment, end_vtx)
        if segment.next[right_side] == segment:
            end_vtx = 0
            return self.rm_dendrite(segment, end_vtx)

        if segment.is_dendrite():
            # dendrite -> split wire
            self._split_wire(segment)
        else:
            # different wires -> join polygons
            self._join_poly(segment)


    # Helper change operations.
    def _append_segment(self, seg):
        seg.vtxs[0].join_segment(seg)
        seg.vtxs[1].join_segment(seg)
        self.segments.append(seg)
        self.pt_to_seg[ seg.vtxs_ids() ] = seg

    def _remove_segment(self, seg):
        seg.vtxs[0].rm_segment(seg)
        seg.vtxs[1].rm_segment(seg)
        del self.pt_to_seg[ seg.vtxs_ids() ]
        del self.segments[seg.id]



    # Special getters.







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
        poly.free_points[pt.id] = pt
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
        if t_point < self.tolerance:
            return seg.vtxs[0]
        elif t_point > 1.0 - self.tolerance:
            return seg.vtxs[1]


        xy_point = seg.parametric(t_point)
        mid_pt = Point(xy_point, None)
        self.points.append(mid_pt)

        b_seg_insert = seg.vtx_insert_info(1)
        # TODO: remove this hard wired insert info setup
        # modify point insert method to return full insert info
        # it should have treatment of the single segment pint , i.e. tip
        seg_tip_insert = (seg, seg, left_side, seg.wire[right_side])
        seg.disconnect_vtx(1)


        new_seg = Segment((mid_pt, seg.vtxs[1]))
        self._append_segment(new_seg)
        seg.vtxs[1] = mid_pt
        new_seg.connect_vtx(0, seg_tip_insert)
        if b_seg_insert[0] is None:
            assert seg.wire[0] == seg.wire[1]
            new_seg.connect_free_vtx(1, seg.wire[0])
        else:
            new_seg.connect_vtx(1, b_seg_insert)

        return mid_pt


    def _join_segments(self, mid_point, seg0, seg1):
        assert mid_point.segment == seg0 or mid_point.segment == seg1
        # TODO: implement segment inversion and allow joining of any two segments
        assert seg0.point[1] == mid_point
        assert seg1.point[0] == mid_point

        # Assert that no other segments are joined to the mid_point
        assert seg0.next[left_side] == seg1
        assert seg1.next[right_side] == seg0

        b_seg1_insert = seg1.vtx_inseert_info(1)
        seg1.disconnect(1)
        seg1.disconnect(0)
        seg0.vtxs[1] = seg1.vtxs[1]
        seg0.connect_vtx(1, b_seg1_insert)

        # fix possible polygon references
        for side in [left_side, right_side]:
            wire = seg1.wire[side]
            if wire.segment == seg1:
                wire.segment = seg0

        self._remove_segment(seg1)
        del self.points[mid_point.id]

    def _new_wire(self, polygon, a_pt, b_pt):
        del polygon.free_points[a_pt.id]
        del polygon.free_points[b_pt.id]
        wire = Wire()
        wire.polygon = polygon
        seg = Segment((a_pt, b_pt))
        seg.connect_free_vtx(0, wire)
        seg.connect_free_vtx(1, wire)
        wire.segment = seg
        wire.parent = polygon.outer_wire
        self._append_segment(seg)
        self.wires.append(wire)
        polygon.holes[wire.id] = wire
        return seg

    def _rm_wire(self, segment):
        assert segment.next[0] == segment and segment.next[1] == segment
        assert segment.wire[0] == segment.wire[1]
        wire = segment.wire[0]
        polygon = wire.polygon
        del polygon.holes[wire.id]
        del self.wires[wire.id]
        self._remove_segment(segment)


    def _wire_add_dendrite(self, root_pt, r_insert, free_pt):
        polygon = free_pt.poly
        r_prev, r_next, r_side, wire = r_insert
        assert wire.polygon == free_pt.poly
        del polygon.free_points[free_pt.id]

        seg = Segment( (root_pt, free_pt))
        self._append_segment(seg)
        seg.connect_vtx(0, r_insert)
        seg.connect_free_vtx(1, wire)
        return seg

    def _wire_rm_dendrite(self, segment, tip_vtx):
        root_vtx = 1 - tip_vtx
        assert segment.wire[0] == segment.wire[1]
        segment.disconnect_vtx(root_vtx)
        segment.disconnect_wires()
        self._remove_segment(segment)

    def _join_wires(self, a_pt, b_pt, a_insert, b_insert):
        """
        Join two wires of the same polygon by new segment.
        """
        a_prev, a_next, a_side, a_wire = a_insert
        b_prev, b_next, b_side, b_wire = b_insert
        assert a_wire != b_wire
        assert a_wire.polygon == b_wire.polygon

        # set next links
        new_seg = Segment( (a_pt, b_pt), (a_wire, a_wire))
        new_seg.connect_vtx(0, a_insert)
        new_seg.connect_vtx(1, (b_prev, b_next, b_side, a_wire) )

        #set wire links
        for seg, side in b_wire.segments(start_segment=new_seg, end_segment=new_seg):
            assert seg.wire[side] == b_wire
            seg.wire[side] = a_wire

        # remove b_wire
        if a_wire.polygon.outer_wire == b_wire:
            a_wire.polygon.outer_wire = a_wire
        else:
            del a_wire.polygon.holes[b_wire.id]
        del self.wires[b_wire.id]
        return new_seg


    def _split_wire(self, segment):
        """
        Remove segment that connects two wires.
        """
        assert segment.wire[0] == segment.wire[1]
        a_wire = segment.wire[0]
        polygon = a_wire.polygon
        b_wire = Wire()
        self.wires.append(b_wire)

        # set new wire to segments
        b_vtx_next_side = Segment.vtx_next_side(1)
        b_next_seg = segment.next[b_vtx_next_side]
        for seg, side in a_wire.segments(start_segment=b_next_seg, end_segment=segment):
            assert seg.wire[side] == a_wire
            seg.wire[side] = b_wire

        segment.disconnect(0)
        segment.disconnect(1)
        segment.disconnect_wires()

        # setup new b_wire
        b_wire.segment = b_next_seg
        b_wire.polygon = a_wire.polygon
        if polygon.outer_wire == a_wire:
            # one wire inside other
            if a_wire.contains(b_wire):
                polygon.outer_wire = a_wire
                b_wire.parent = a_wire
                polygon.holes[b_wire.id] = b_wire
            else:
                polygon.outer_wire = b_wire
                b_wire.parent = a_wire.parent
                a_wire.parent = b_wire
                polygon.holes[a_wire.id] = a_wire
        else:
            # both wires are holes
            b_wire.parent = a_wire.parent
            polygon.holes[b_wire.id] = b_wire

        # remove segment
        self._remove_segment(segment)



    def _split_poly(self, a_pt, b_pt, a_insert, b_insert):
        """
        Split polygon by new segment.
        """
        a_prev, a_next, a_side, a_wire = a_insert
        b_prev, b_next, b_side, b_wire = b_insert
        assert a_wire == b_wire

        left_wire = a_wire
        right_wire = Wire()
        self.wires.append(right_wire)

        # set next links
        new_seg = Segment( (a_pt, b_pt))
        self.segments.append(new_seg)
        new_seg.connect_vtx(0, a_insert)
        new_seg.connect_vtx(1, (b_prev, b_next, b_side, right_wire))

        # set right_wire links
        for seg, side in b_wire.segments(start_segment=new_seg.next[right_side], end_segment=new_seg):
            assert seg.wire[side] == a_wire
            seg.wire[side] = right_wire
        left_wire.segment = right_wire.segment = new_seg

        # update polygons
        left_poly = left_wire.polygon
        right_poly = Polygon(b_wire)
        self.polygons.append(right_poly)

        if a_wire.polygon.outer_wire == a_wire:
            # two disjoint polygons
            right_poly.outer_wire = right_wire
            right_wire.polygon = right_poly
            right_wire.parent = a_wire.parent

        else:
            # two embedded wires/polygons
            if left_wire.contains(right_wire):
                right_poly.outer_wire = right_wire
                right_wire.parent = left_wire
                right_wire.polygon = right_poly
            else:
                right_wire.parent = left_wire.parent
                left_wire.parent = right_wire
                right_wire.polygon = left_poly
                left_wire.polygon = right_poly
                right_poly.outer_wire = left_wire

        # split free points
        for pt in left_poly.free_points.values():
            if right_poly.outer_wire.contains_point(pt):
                right_poly.free_points[pt.id] = left_poly.free_points.pop(pt.id)

        # split holes
        for hole in left_poly.holes.values():
            if right_poly.outer_wire.contains_wire(hole):
                right_poly.holes[hole.id] = left_poly.holes.pop(hole.id)
        return new_seg


    def _joint_poly(self, segment):
        """
        Join polygons by removing a segment.
        """
        pass





# Data classes contains no modification methods, all modifications are through reversible atomic operations.
class Point:
    def __init__(self, point, poly):
        self.id = id
        self.xy = np.array(point)
        self.poly = poly
        # Containing polygon for free-nodes. None for others.
        self.segment = None
        # One of joined segments for non-free nodes. None for the free ones.


    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "pt id: {} xy: {}".format(self.id, self.xy)

    def is_free(self):
        return self.segment is  None

    def is_outgoing(self, segment):
        return self == segment.vtxs[0]

    def magnitude(self):
        return la.norm(self.xy, np.inf)

    def segments(self, start_segment=None ):
        """
        Generator for segments joined to the point.
        yields: (segment, vtx_idx), where vtx_idx is index of 'point' in 'segment'
        """
        if start_segment is None:
            start_segment = self.segment
        if start_segment is None:
            return
        seg = start_segment
        while (1):
            yield seg
            outgoing = self.is_outgoing(seg)
            next_side = right_side if outgoing else left_side
            seg = seg.next[next_side]
            if seg == start_segment:
                return


    def insert_segment(self, vector):
        vec_angle =  np.angle(complex(vector[0], vector[1]))
        last = None
        for seg in self.segments():
            seg_vec = seg.vector()
            if not self.is_outgoing(seg):
                seg_vec *= -1.0
            angle = np.angle(complex(seg_vec[0], seg_vec[1]))
            da = angle - vec_angle
            if da < 0.0:
                da += 2*np.pi
            if last and da > last[1]:
                prev = last[0]
                next = seg
                break

            last = (seg, da)
        else:
            if last:
                prev = next = last[0]
            else:
                # for free point
                return (None, None, None, None)
        prev_side = prev.previous_side(self)
        wire = prev.wire[prev_side]
        return (prev, next, prev_side, wire)



    def join_segment(self, seg):
        if self.is_free():
            self.poly = None
            self.segment = seg


    def rm_segment(self, seg):
        if self.segment == seg:
            for new_seg in self.segments():
                if not new_seg == seg:
                    self.segment = new_seg
                    return
            assert seg.is_dendrite()
            self.poly = seg.wire[0].polygon
            self.segment = None



class Segment:
    def __init__(self, vtxs):
        self.id = id
        self.vtxs = list(vtxs)
        # tuple (start, end) point object
        self.wire = [None, None]
        # (left_poly, right_poly) - polygons on left and right side
        #self.ori = ori
        # (left_ori, right_ori); indicator if segment orientation match ccwise direction of the polygon
        #self.prev = prev
        # (left_prev, right_prev);  previous edge for left and right side;
        self.next = [None, None]
        # (left_next, right_next); next edge for left and right side;

    def __repr__(self):
        return "Segment id: {} v0: {}  v1: {} next: {}".format(self.id, self.vtxs[0], self.vtxs[1], [self.next[0].id, self.next[1].id] )

    @staticmethod
    def side_to_vtx(side, side_vtx):
        assert left_side == 0
        assert right_side == 1
        tab = [ [0,1], [1,0]]
        return tab[side][side_vtx]

    @staticmethod
    def vtx_next_side(vtx_idx):
        return [right_side, left_side][vtx_idx]

    def set_next(self, left, right):
        self.set_next_side(left_side, left)
        self.set_next_side(right_side, right)

    def set_next_side(self, side, next_seg):
        self.next[side] = next_seg
        side_next_vtx = self.vtxs[ self.side_to_vtx(side, 1) ]
        assert self.next[side].have_vtx(side_next_vtx)

    def have_vtx(self, pt):
        return self.vtxs[0] == pt or self.vtxs[1] == pt


    def connect_vtx(self, vtx_idx, insert_info):
        self.vtxs[vtx_idx].join_segment(self)
        prev, next, prev_side, wire = insert_info
        next_side = self.vtx_next_side(vtx_idx)
        self.set_next_side(next_side, next)
        prev.set_next_side(prev_side, self)
        self.wire[next_side] = wire
        #assert prev.wire[prev_side] == wire

    def connect_free_vtx(self, vtx_idx, wire):
        self.vtxs[vtx_idx].join_segment(self)
        next_side = self.vtx_next_side(vtx_idx)
        self.set_next_side(next_side, self)
        self.wire[next_side] = wire

    def vtx_insert_info(self, vtx_idx):
        """
        Return insert info for connecting after disconnect.
        """
        side_next = Segment.vtx_next_side(vtx_idx)
        next = self.next[ side_next ]
        if next == self:
            return (None, None, None, None)
        wire = self.wire[ side_next ]

        side_prev = Segment.vtx_next_side(1- vtx_idx) # prev side is next side of oposite vertex
        prev, prev_side = self.previous(side_prev)
        return (prev, next, prev_side, wire)

    def disconnect_vtx(self, vtx_idx):
        self.vtxs[vtx_idx].rm_segment(self)
        seg_side_prev = Segment.vtx_next_side(1-vtx_idx)
        seg_side_next = Segment.vtx_next_side(vtx_idx)

        prev_seg, prev_side = self.previous(seg_side_prev)
        prev_seg.next[prev_side] = self.next[seg_side_next]
        self.next[seg_side_next] = self

    def disconnect_wires(self):
        for side in [left_side, right_side]:
            wire = self.wire[side]
            if wire.segment == self:
                next_seg = self.next[side]
                wire.segment = next_seg
                assert wire == next_seg.wire[0] or wire == next_seg.wire[1]

    def contains_point(self, pt):
        Dxy = self.vector()
        axis = np.argmax(Dxy)
        D = Dxy[axis]
        magnitude = max([self.vtxs[0].xy[axis], self.vtxs[1].xy[axis] ])
        assert np.abs(D) > 1e-12 * (1.0 + magnitude)
        t = (pt[axis] - self.vtxs[0].xy[axis]) / D
        if 0 <= t <= 1:
            xy = self.parametric(t)
            if la.norm(pt - xy, np.inf) < 1e-3 * D:
                return t
            else:
                return None
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
        eps = 1e-10
        if 0 <= t0 <= 1  and 0 + eps <= t1 <= 1 - eps:
            return (t0, t1)
        else:
            return (None, None)

    def x_line_isec(self, xy):
        vtxs = np.array([self.vtxs[0].xy, self.vtxs[1].xy])
        Dy = vtxs[1, 1] - vtxs[0, 1]
        magnitude = np.max(vtxs[:, 1])
        # require at least 4 decimal digit remaining precision of the Dy
        if np.abs(Dy) < 1e-12 * (1.0 + magnitude):
            # horizontal edge
            return [ vtxs[0, 0], vtxs[1, 0] ]
        else:
            t = (xy[1] - vtxs[0, 1]) / Dy
            if 0 < t <= 1:
                Dx = vtxs[1, 0] - vtxs[0, 0]
                isec_x = t * Dx + vtxs[0, 0]
                return [isec_x]
            else:
                return []

    def is_on_x_line(self, xy):
        """
        TODO: Careful test of numerical stability when x_axis goes through
        a point or a segment is on it.
        :param xy:
        :return:
        """
        x_isec = self.x_line_isec(xy)
        x_isec.append(xy[0])
        if min( x_isec )  > xy[0]:
            return True
        return False

    # def is_vertex(self, point):
    #     if point == self.points[0]:
    #          return 0
    #     if point == self.points[1]:
    #         return 1
    #     return None

    def vtxs_ids(self):
        return (self.vtxs[0].id, self.vtxs[1].id)

    def __eq__(self, other):
        return self.id == other.id

    def is_dendrite(self):
        return self.wire[left_side] == self.wire[right_side]

    def vector(self):
        return (self.vtxs[1].xy - self.vtxs[0].xy)

    def parametric(self, t):
        return  self.vector() * t + self.vtxs[0].xy

    def previous(self, side):
        """
        Oposite of seg.next[side]. Implemented through loop around a node.
        :param seg:
        :param side:
        :return:
        """
        vtx_idx = Segment.side_to_vtx(side, 0)
        vtx = self.vtxs[vtx_idx]
        for seg in vtx.segments(start_segment = self):
            pass
        prev_side = seg.previous_side(vtx)
        return (seg, prev_side)

    def previous_side(self, point):
        if self.vtxs[0] == point:
            return right_side
        else:
            assert self.vtxs[1] == point
            return left_side

class Wire:
    def __init__(self):
        self.parent = None
        # Wire that contains this wire. None for the global outer boundary.
        # Parent relations are independent of polygons.
        self.polygon = None
        # Polygon of this wire
        self.segment = None
        # One segment of the wire.

    def __eq__(self, other):
        # None is wire in infinity
        if self is None or other is None:
            return False
        return self.id == other.id


    def segments(self, start_segment = None, end_segment = None):
        if start_segment is None:
            start_segment = self.segment
        if end_segment is None:
            end_segment = self.segment

        seg = start_segment
        visited = []
        while (1):
            side = left_side if seg.wire[left_side] == self else right_side
            visited.append( (seg, side) )
            yield (seg, side)
            seg = seg.next[side]
            if seg == end_segment:
                break
            if seg.id in [s.id for s,ss in visited]:
                print(visited)
                assert False, "Repeated seg: {}".format(seg)
            assert not seg == start_segment, "Inifinite loop."

    def outer_segments(self):
        """
        :return: List of boundary componencts without tails. Single component is list of segments (with orientation)
        that forms outer boundary, i.e. excluding internal tails, i.e. segments appearing just once.
        """
        for seg, side  in self.segmets():
            if not seg.is_dendrite():
                yield (seg, side)


    def contains(self, wire):
        if self is None:
            return True
        if wire is None:
            return False
        # test if a point of wire is inside 'self'
        seg = wire.segment
        tang = seg.vector()
        norm = tang[[1,0]]
        norm[0] = -norm[0]  # left side normal
        if wire == seg.wire[right_side]:
            norm = -norm
        eps = 1e-10     # TODO: review this value to be as close to the line as possible while keep intersection work
        inner_point = seg.vtxs[0].xy + 0.5 * tang  + eps * norm
        n_isec = 0
        for seg, side in self.segments():
            n_isec += int(seg.is_on_x_line(inner_point))
        if n_isec % 2 == 1:
            return True
        else:
            return False

class Polygon:
    def __init__(self, outer_wire):
        self.outer_wire = outer_wire
        # outer boundary wire
        self.holes = {}
        # Wires of holes.
        self.free_points = {}
        # Dict ID->pt of free points inside the polygon.


    def __eq__(self, other):
        return self.id == other.id


