import numpy as np
import bisect
import numpy.linalg as la
import enum

# TODO: rename point - > node
# TODO: Change points, segments, wires, polygons, holes, free_points to sets where it is appropriate.
# TODO: careful unification of tolerance usage.
# TODO: Review segment snapping to snap in normal direction.
# TODO: Performance tests:
# - snap_point have potentialy very bad complexity O(Nlog(N)) with number of segments
# - add_line linear with number of segments
# - other operations are at most linear with number of segments per wire or point

# TODO: Reconstruction just from list of points, segments and polygons.
# TODO: Reconstruction from Point.xy; Semgnet.(vtxs, next); Wire.(segment,  parent); Polygon.(outer, holes, free_points)



in_vtx = left_side = 1
# vertex where edge comes in; side where next segment is connected through the in_vtx
out_vtx = right_side = 0
# vertex where edge comes out; side where next segment is connected through the out_vtx


class IdObject:
    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


class IdMap(dict):
    id = 0

    def get_new_id(self):
        if not hasattr(self, '_next_id'):
            self._next_id = 0
        self._next_id += 1
        return self._next_id

    def append(self, obj, id = None):
        if id is None:
            id = self.get_new_id()
        obj.id = id
        self[obj.id] = obj
        return obj


class PolygonChange(enum.Enum):
    none=0
    shape=1
    add=2
    remove=3
    split=4
    join=5


class PolygonDecomposition:
    """
    Decomposition of a plane into (non-convex) polygonal subsets (not necessarily domains).
    """

    def __init__(self):
        """
        Constructor.
        PUBLIC: outer_polygon_id
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
        outer_wire = self.wires.append(Wire())
        outer_wire.parent = None
        self.outer_polygon = Polygon(outer_wire)
        self.polygons.append(self.outer_polygon)
        outer_wire.polygon = self.outer_polygon


        self.last_polygon_change=(PolygonChange.add, self.outer_polygon, self.outer_polygon)
        # add outer polygon
        #
        self.tolerance = 0.01


    def __repr__(self):
        stream = ""
        for label, objs in [ ("Polygons:", self.polygons), ("Wires:", self.wires), ("Segments:", self.segments)]:
            stream += label + "\n"
            for obj in objs.values():
                stream += str(obj) + "\n"
        return stream


    ##################################################################
    # Interface for LayerEditor.
    ##################################################################
    def add_free_point(self, point_id, xy, polygon_id):
        """
        LAYERS
        :param: ID of point to add.
        :param: point: (X,Y)
        :return: Point instance
        """
        polygon = self.polygons[polygon_id]
        self._add_free_point(xy, polygon, id = point_id)


    def remove_free_point(self, point_id):
        """
        LAYERS
        :param: point_id - ID of free point to remove
        :return: None
        """
        point = self.points[point_id]
        self._remove_free_point(point)

    def new_segment_ids(self, a_pt_id, b_pt_id):
        a_pt = self.points[a_pt_id]
        b_pt = self.points[b_pt_id]
        self.new_segment(a_pt, b_pt)

    def new_segment(self, a_pt, b_pt):
        """
        LAYERS
        Add segment between given existing points. Assumes that there is no intersection with other segment.
        Just return the segment if it exists.
        :param a_pt: Start point of the segment.
        :param b_pt: End point.
        :return: new segment
        """
        self.last_polygon_change = (PolygonChange.none, None, None)
        segment = self.pt_to_seg.get((a_pt.id, b_pt.id), None)
        if segment is not None:
            return segment
        segment = self.pt_to_seg.get((b_pt.id, a_pt.id), None)
        if segment is not None:
            return segment

        if a_pt.is_free() and b_pt.is_free():
            assert a_pt.poly == b_pt.poly
            return self._new_wire(a_pt.poly, a_pt, b_pt)

        vec = b_pt.xy - a_pt.xy
        a_insert = a_pt.insert_segment(vec)
        b_insert = b_pt.insert_segment(-vec)

        if a_pt.is_free():
            assert b_insert is not None
            return self._wire_add_dendrite( (a_pt, b_pt), b_insert, in_vtx)
        if b_pt.is_free():
            assert a_insert is not None
            return self._wire_add_dendrite( (a_pt, b_pt), a_insert, out_vtx)

        assert a_insert is not None
        assert b_insert is not None
        a_prev, a_next, a_wire = a_insert
        b_prev, b_next, b_wire = b_insert

        if a_wire != b_wire:
            return self._join_wires(a_pt, b_pt, a_insert, b_insert)
        else:
            return self._split_poly(a_pt, b_pt, a_insert, b_insert)


    def delete_segment(self, segment):
        """
        LAYERS
        Remove specified segment.
        :param segment:
        :return: None
        """
        self.last_polygon_change = (PolygonChange.none, None, None)
        left_self_ref = segment.next[left_side] == (segment, right_side)
        right_self_ref = segment.next[right_side] == (segment, left_side)
        # Lonely segment, both endpoints are free.
        if left_self_ref and right_self_ref:
            return self._rm_wire(segment)
        # At least one free endpoint.
        if left_self_ref:
            return self._wire_rm_dendrite(segment, in_vtx)
        if right_self_ref:
            return self._wire_rm_dendrite(segment, out_vtx)

        # Both endpoints connected.
        if segment.is_dendrite():
            # Same wire from both sides. Dendrite.
            self._split_wire(segment)
        else:
            # Different wires.
            self._join_poly(segment)


    def check_displacment(self, points, displacement, margin):
        """
        LAYERS
        param: points: List of Points to move.
        param: displacement: Numpy array, 2D vector of displacement to add to the points.
        param: margin: float between (0, 1), displacement margin as a fraction of maximal displacement
        :return: Shortened displacement to not cross any segment.
        """
        # Collect fixed sides of segments connecting fixed and moving point.
        segment_set = set()
        changed_polygons = set()
        for pt in points:
            for seg, side in pt.segments():
                changed_polygons.add(seg.wire[out_vtx].polygon)
                changed_polygons.add(seg.wire[in_vtx].polygon)
                opposite = (seg, 1-side)
                if opposite in segment_set:
                    segment_set.remove(opposite)
                else:
                    segment_set.add((seg, side))

        # collect segments fomring envelope(s) of the moving points
        envelope = set()
        for seg, side in segment_set:
            for e_seg_side in seg.wire[side].segments(start = seg.next[side]):
                if e_seg_side in segment_set:
                    break
                e_seg, e_side = e_seg_side
                envelope.add(e_seg)

        new_displ = np.array(displacement)
        for seg in envelope:
            for pt in points:
                (t0, t1) = seg.intersection(pt.xy, pt.xy + new_displ)
                # TODO: Treat case of vector and segment in line.
                # TODO: Check bound checks in intersection.
                if t0 is not None:
                    new_displ *= (1.0 - margin) * t1
        self.last_polygon_change = (PolygonChange.shape, changed_polygons, None)
        return new_displ

    def move_points(self, points, displacement):
        """
        Move given points by given displacement vector. Assumes no intersections. But possible
        segment splitting (add_point is called).
        param: points: List of Points to move.
        param: displacement: Numpy array, 2D vector of displacement to add to the points.
        :return: None
        """
        for pt in points:
            pt.xy += displacement


    def get_last_polygon_changes(self):
        """
        LAYERS
        Return information about polygon changes during last new_segment or delete_segment operations.
        :return: ( PolygonChange, p0.id, p1.id)
        cases:
        (PolygonChange.none, None, None) - no change in any polygon, already existed segment
        (PolygonChange.shape, list_poly_id, None) - list of polygons that have changed shape, e.g. add/remove dendrite
        (PolygonChange.add, orig_poly_id, new_poly_id) - new polygon inside other polygon
        (PolygonChange.remove, orig_poly_id, new_poly_id) - deleted polygon inside other polygon
        (PolygonChange.split, orig_poly_id, new_poly_id) - split new_poly from orig_poly
        (PolygonChange.join, orig_poly_id, new_poly_id) - join both polygons into orig_poly

        After init of PolygonDecomposition this method returns:
        (PolygonChange.add, outer_polygon_id, outer_polygon_id)
        """
        type, p0, p1 = self.last_polygon_change
        if type == PolygonChange.shape:
            poly_ids = [ p.id for p in p0 ]
            return (type, poly_ids, None)
        id0 = None if p0 is None else p0.id
        id1 = None if p1 is None else p1.id
        return (type, id0, id1)

    def get_childs(self, polygon_id):
        """
        Return list of child ploygons (including itself).
        :param polygon_id:
        :return: List of polygon IDs.
        """
        root_poly = self.polygons[polygon_id]
        for poly in  root_poly.child_polygons():
            yield poly.id

    ########################################
    # Other public methods.

    def set_tolerance(self, tolerance):
        """
        Set tolerance for snapping to existing points and lines.
        Should be given by actual zoom level.
        :param tolerance: float, a distance used to snap points to existing objects.
        :return: None
        """
        self.tolerance = tolerance


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
        for seg in self.segments.values():
            x_isec = seg.x_line_isec(point, self.tolerance)
            for x_isec_pt in x_isec:
                x_axis_segs.append((x_isec_pt, seg.id, seg))

        if len(x_axis_segs) == 0:
            return self._snap_to_polygon(self.outer_polygon, point)
        x_axis_segs.sort()
        i = bisect.bisect_left(x_axis_segs, (x_pt, seg.id, seg))
        # i ...  x_axis_segs[i-1] < x_pt <= x_axis_segs[i]

        assert i <= len(x_axis_segs)
        idx_set = [ (max(i-1, 0), False), (min(i, len(x_axis_segs)-1), True) ]
        for j, up in idx_set:
            px, id, seg = x_axis_segs[j]
            snapped = self._snap_to_segment(seg, point, up_is_left=up)
            if snapped[0] < 2:
                return snapped
            wire = snapped[1]
        return self._snap_to_polygon(wire.polygon, point)


    def _snap_to_segment(self, segment, point, up_is_left ):
        """
        Snap to segment or to its side wire.
        Auxiliary method for 'snap_point'.
        :return: see: snap_point
        """
        tt = segment.contains_point(point, self.tolerance)
        if tt is not None:
            if segment.vtxs[out_vtx].colocated(segment.parametric(tt), self.tolerance):
                return (0, segment.vtxs[out_vtx], None)
            if segment.vtxs[in_vtx].colocated(segment.parametric(tt), self.tolerance):
                return (0, segment.vtxs[in_vtx], None)
            return (1, segment, tt)
        else:
            up_ori = segment.vtxs[in_vtx].xy[1] > segment.vtxs[out_vtx].xy[1]
            if up_ori == up_is_left:
                side = left_side
            else:
                side = right_side
            wire = segment.wire[side]
            return (2, wire, None)

    def _snap_to_polygon(self, polygon, point):
        for pt in polygon.free_points.values():
            if pt.colocated(point, self.tolerance):
                return (0, pt, None)
        return (2, polygon, None)





    ###################################################################
    # Macro operations that change state of the decomposition.
    def add_point(self, point):
        """
        Try to add a new point, snap to lines and existing points.
        :param point: numpy array with XY coordinates
        :return: Point instance.

        This operation translates to atomic operations: add_free_point and split_line_by_point.
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
        call add_point for endpoints, call split_segment for intersections, then call operation new_segment for individual
        segments.
        :param a: numpy array X, Y
        :param b: numpy array X, Y
        :return: List of subdivided segments. Split segments are not reported.
        """
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        a_point = self.add_point(a)
        b_point = self.add_point(b)


        seg_list = []
        for seg in self.segments.values():
            (t0, t1) = seg.intersection(a, b)
            if t1 is not None:
                seg_list.append((seg, t0, t1))
        t_list = []
        for seg, t0, t1 in seg_list:
            mid_pt = self._split_segment(seg, t0)
            t_list.append( (t1, mid_pt) )
        t_list.sort()   # sort by t1
        start_pt = a_point
        result = []
        for t1, mid_pt in t_list:
            result.append( self.new_segment(start_pt, mid_pt) )
            start_pt = mid_pt
        result.append( self.new_segment(start_pt, b_point) )
        return result





    def delete_point(self, point):
        """
        Delete given point with all connected segments.
        :param point:
        :return:
        """
        segs_to_del = [ seg for seg, side in point.segments()]
        for seg in segs_to_del:
            self.delete_segment(seg)
        self._remove_free_point(point)


    def make_indices(self):
        """
        Asign index to every node, segment and ppolygon.
        :return: None
        """
        for collection in [self.points, self.segments, self.polygons]:
            for idx, obj in enumerate(collection.values()):
                obj.index = idx



    def make_wire_from_segments(self, seg_ids, polygon):
        """
        Set half segments of the wire, and the wire itself.
        :param seg_ids: Segment ids, at least 2 and listed in the orientation matching the wire (cc wise)
        :param polygon: Polygon the wire is part of.
        :return: None
        """
        assert len(seg_ids) >= 2
        wire = Wire()
        self.wires.append(wire)

        # detect orientation of the first segment
        seg0 = self.segments[seg_ids[0]]
        seg1 = self.segments[seg_ids[1]]
        vtx0_side = seg1.point_side(seg0.vtxs[out_vtx])
        if vtx0_side is None:
            assert seg1.point_side(seg0.vtxs[in_vtx]) is not None, "Can not connect segments: {} {}".format(seg0.id, seg1.id)
            side0 = in_vtx
        else:
            side0 = out_vtx
        seg_side_0 = (seg0, side0)

        # set segment sides along the wire
        for id in seg_ids:
            seg = self.segments[id]
            side = seg.point_side(seg0.vtxs[side0])
            assert side is not None, "Can not connect segments: {} {}".format(seg0.id, seg.id)
            seg0.next[side0] = (seg, side)
            seg0.wire[side0] = wire
            seg0, side0 = seg, side
        seg0.next[side0] = seg_side_0
        seg0.wire[side0] = wire
        wire.segment = seg_side_0
        wire.polygon = polygon

    def finish_setup(self):
        """
        - set back links from points to segments or polygons
        - check that all segments are set.
        - set parent links of all wires
        :return:
        """
        for seg in self.segments.values():
            for side in [out_vtx, in_vtx]:
                seg.vtxs[side].segment = (seg, side)
            assert None not in seg.wire
            assert None not in seg.next
        self.set_wire_parents(self.outer_polygon, self.outer_polygon.outer_wire)

    def set_wire_parents(self, polygon, parent_wire):
        """
        Recursively set parent wire links from holes.
        :param polygon: Which polygon's holes to set.
        :param parent_wire: parent wire to set to holes.
        :return: None
        """
        for hole_wire in polygon.outer_wire.childs:
            hole_wire.set_parent(parent_wire)
            seg, side  = hole_wire.segment
            other_wire = seg.wire[1 - side]
            if not other_wire == hole_wire:
                other_poly = other_wire.polygon
                other_poly.outer_wire = hole_wire
                self.set_polygon_parents(other_poly, hole_wire)




    # Reversible atomic change operations.
    # TODO: Add history notifiers to the return point.

    def _add_free_point(self, point, poly, id=None):
        """
        :param point: XY array
        :return: Point instance
        """

        pt = Point(point, poly)
        if id is None:
            self.points.append(pt)
        else:
            self.points.append(pt, id)
        poly.free_points[pt.id] = pt
        return pt


    def _remove_free_point(self, point):
        assert point.poly is not None
        assert point.segment[0] is None
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
            return seg.vtxs[out_vtx]
        elif t_point > 1.0 - self.tolerance:
            return seg.vtxs[in_vtx]


        xy_point = seg.parametric(t_point)
        mid_pt = Point(xy_point, None)
        self.points.append(mid_pt)

        b_seg_insert = seg.vtx_insert_info(in_vtx)
        # TODO: remove this hard wired insert info setup
        # modify point insert method to return full insert info
        # it should have treatment of the single segment pint , i.e. tip
        seg_tip_insert = ( (seg, left_side), (seg, right_side), seg.wire[right_side])
        seg.disconnect_vtx(in_vtx)

        new_seg = self._make_segment((mid_pt, seg.vtxs[in_vtx]))
        seg.vtxs[in_vtx] = mid_pt
        new_seg.connect_vtx(out_vtx, seg_tip_insert)
        if b_seg_insert is None:
            assert seg.is_dendrite()
            new_seg.connect_free_vtx(in_vtx, seg.wire[left_side])
        else:
            new_seg.connect_vtx(in_vtx, b_seg_insert)

        return mid_pt


    def _join_segments(self, mid_point, seg0, seg1):
        """
        TODO: replace by del_segment and 2x new_segment
        """
        if seg0.vtxs[in_vtx] == mid_point:
            seg0_out_vtx, seg0_in_vtx = out_vtx, in_vtx
        else:
            seg0_out_vtx, seg0_in_vtx = in_vtx, out_vtx

        if seg1.vtxs[out_vtx] == mid_point:
            seg1_out_vtx, seg1_in_vtx = out_vtx, in_vtx
        else:
            seg1_out_vtx, seg1_in_vtx = in_vtx, out_vtx

        # Assert that no other segments are joined to the mid_point
        assert seg0.next[seg0_in_vtx] == (seg1, seg1_in_vtx)
        assert seg1.next[seg1_out_vtx] == (seg0, seg0_out_vtx)

        b_seg1_insert = seg1.vtx_insert_info(seg1_in_vtx)
        seg1.disconnect_vtx(seg1_in_vtx)
        seg1.disconnect_vtx(seg1_out_vtx)
        seg0.disconnect_vtx(seg0_in_vtx)
        seg0.vtxs[seg0_in_vtx] = seg1.vtxs[seg1_in_vtx]
        if b_seg1_insert is None:
            assert seg0.is_dendrite()
            seg0.connect_free_vtx(seg0_in_vtx, seg0.wire[out_vtx])
        else:
            seg0.connect_vtx(seg0_in_vtx, b_seg1_insert)

        # fix possible wire references
        for side in [left_side, right_side]:
            wire = seg1.wire[side]
            if wire.segment == (seg1, side):
                wire.segment = (seg0, side)

        self._destroy_segment(seg1)
        self._remove_free_point(mid_point)

    def _new_wire(self, polygon, a_pt, b_pt):
        """
        New wire containing just single segment.
        return the new_segment
        """

        #del polygon.free_points[a_pt.id]
        #del polygon.free_points[b_pt.id]
        wire = self.wires.append(Wire())
        wire.polygon = polygon
        wire.set_parent(polygon.outer_wire)
        seg = self._make_segment((a_pt, b_pt))
        seg.connect_free_vtx(out_vtx, wire)
        seg.connect_free_vtx(in_vtx, wire)
        wire.segment = (seg, right_side)
        return seg

    def _rm_wire(self, segment):
        """
        Remove the last segment of a wire.
        :return: None
        """
        assert segment.next[left_side] == (segment, right_side) and segment.next[right_side] == (segment, left_side)
        assert segment.is_dendrite()
        wire = segment.wire[left_side]
        polygon = wire.polygon
        polygon.outer_wire.childs.remove(wire)
        del self.wires[wire.id]
        self._destroy_segment(segment)


    def _wire_add_dendrite(self, points, r_insert, root_idx):
        """
        Add new dendrite tip segment.
        points: (out_pt, in_pt)
        r_insert: insert information for root point
        root_idx: index (0/1) of the root, i.e. non-free point.
        """
        free_pt = points[1-root_idx]
        polygon = free_pt.poly
        r_prev, r_next, wire = r_insert
        assert wire.polygon == free_pt.poly
        #del polygon.free_points[free_pt.id]

        seg = self._make_segment( points)
        seg.connect_vtx(root_idx, r_insert)
        seg.connect_free_vtx(1-root_idx, wire)
        self.last_polygon_change = (PolygonChange.shape, [polygon], None)
        return seg

    def _wire_rm_dendrite(self, segment, tip_vtx):
        """
        Remove dendrite tip segment.
        """

        root_vtx = 1 - tip_vtx
        assert segment.is_dendrite()
        polygon = segment.wire[out_vtx].polygon
        segment.disconnect_vtx(root_vtx)
        segment.disconnect_wires()
        self._destroy_segment(segment)
        self.last_polygon_change = (PolygonChange.shape, [polygon], None)

    def _join_wires(self, a_pt, b_pt, a_insert, b_insert):
        """
        Join two wires of the same polygon by new segment.
        """
        a_prev, a_next, a_wire = a_insert
        b_prev, b_next, b_wire = b_insert
        assert a_wire != b_wire
        assert a_wire.polygon == b_wire.polygon
        polygon = a_wire.polygon
        self.last_polygon_change = (PolygonChange.shape, [polygon], None)

        # set next links
        new_seg = self._make_segment( (a_pt, b_pt))
        new_seg.connect_vtx(out_vtx, a_insert)
        new_seg.connect_vtx(in_vtx, b_insert)


        ############################
        if polygon.outer_wire == a_wire:
            rm_wire = b_wire
            keep_wire = a_wire
            parent_wire = keep_wire.parent  # parent wire to set for childs of rm_wire
            polygon.outer_wire = keep_wire

        elif polygon.outer_wire == b_wire:
            rm_wire = b_wire
            keep_wire = a_wire
            parent_wire = keep_wire.parent
            polygon.outer_wire = keep_wire
        else:
            rm_wire = b_wire
            keep_wire = a_wire
            parent_wire = keep_wire

        # update segment links to rm_wire
        for seg, side in b_wire.segments(start= (new_seg, in_vtx), end= (new_seg, out_vtx)):
            assert seg.wire[side] == rm_wire, "wire: {} bwire: {} awire{}".format(seg.wire[side], b_wire, a_wire)
            seg.wire[side] = keep_wire
        new_seg.wire[out_vtx] = keep_wire

        # update child links to rm_wire
        for child in list(rm_wire.childs):
             child.set_parent(parent_wire)

        # update parent link to rm_wire
        rm_wire.parent.childs.remove(rm_wire)
        #####################
        del self.wires[rm_wire.id]

        return new_seg


    def _split_wire(self, segment):
        """
        Remove segment that connects two wires.
        """
        """
         Remove segment that connects two wires.
         """
        assert segment.is_dendrite()
        a_wire = segment.wire[left_side]
        polygon = a_wire.polygon
        b_wire = self.wires.append(Wire())

        # set new wire to segments (b_wire is on the segment side of the vtx[1])
        b_vtx_next_side = in_vtx
        b_vtx_prev_side = 1 - b_vtx_next_side
        b_next_seg = segment.next[b_vtx_next_side]
        for seg, side in a_wire.segments(start = b_next_seg, end = (segment, b_vtx_prev_side)):
            assert seg.wire[side] == a_wire
            seg.wire[side] = b_wire

        segment.disconnect_vtx(out_vtx)
        segment.disconnect_vtx(in_vtx)
        segment.disconnect_wires()

        # setup new b_wire
        b_wire.segment = b_next_seg
        b_wire.polygon = a_wire.polygon
        if polygon.outer_wire == a_wire:
            # one wire inside other
            outer_wire, inner_wire = b_wire, a_wire
            if a_wire.contains_wire(b_wire):
                outer_wire, inner_wire = a_wire, b_wire
            polygon.outer_wire = outer_wire
            outer_wire.set_parent(a_wire.parent)  # outer keep parent of original wire
            inner_wire.set_parent(outer_wire)
            self._update_wire_parents(a_wire.parent, a_wire.parent, inner_wire)

        else:
            # both wires are holes
            b_wire.set_parent(a_wire.parent)
            self._update_wire_parents(a_wire, a_wire, b_wire)

        # remove segment
        self.last_polygon_change = (PolygonChange.shape, [polygon], None)
        self._destroy_segment(segment)

    def _update_wire_parents(self, orig_wire, outer_wire, inner_wire):
        # Auxiliary method of _split_wires.
        # update all wires having orig wire as parent
        for wire in self.wires.values():
            if wire.parent == orig_wire:
                if inner_wire.contains_wire(wire):
                    wire.set_parent(inner_wire)
                else:
                    wire.set_parent(outer_wire)


    def _split_poly(self, a_pt, b_pt, a_insert, b_insert):
        """
        Split polygon by new segment.
        """
        a_prev, a_next, a_wire = a_insert
        b_prev, b_next, b_wire = b_insert
        assert a_wire == b_wire
        orig_wire  = a_wire

        right_wire = a_wire
        left_wire = self.wires.append(Wire())

        # set next links
        new_seg = self._make_segment( (a_pt, b_pt))
        new_seg.connect_vtx(out_vtx, a_insert)
        new_seg.connect_vtx(in_vtx, (b_prev, b_next, left_wire))

        # set right_wire links
        for seg, side in orig_wire.segments(start=new_seg.next[left_side], end = (new_seg, left_side)):
            assert seg.wire[side] == orig_wire
            seg.wire[side] = left_wire
        left_wire.segment = (new_seg, left_side)
        right_wire.segment = (new_seg, right_side)

        # update polygons
        orig_poly = right_poly = orig_wire.polygon
        new_poly = Polygon(left_wire)
        self.polygons.append(new_poly)
        left_wire.polygon = new_poly

        if orig_wire.polygon.outer_wire == orig_wire:
            # two disjoint polygons
            new_poly.outer_wire = left_wire
            left_wire.set_parent( orig_wire.parent)
            self.last_polygon_change = (PolygonChange.split, orig_poly, new_poly)
        else:
            assert orig_wire.parent == orig_poly.outer_wire
            # two embedded wires/polygons
            if right_wire.contains_wire(left_wire):
                inner_wire, outer_wire = left_wire, right_wire
            else:
                inner_wire, outer_wire = right_wire, left_wire
            outer_wire.polygon = orig_poly
            inner_wire.polygon = new_poly
            new_poly.outer_wire = inner_wire
            outer_wire.set_parent( orig_wire.parent)
            inner_wire.set_parent( outer_wire )
            self.last_polygon_change = (PolygonChange.add, orig_poly, new_poly)

        # split free points
        for pt in list(orig_poly.free_points.values()):
            if new_poly.outer_wire.contains_point(pt.xy):
                pt.set_polygon(new_poly)

        # split holes
        for hole_wire in list(orig_poly.outer_wire.childs):
            if new_poly.outer_wire.contains_wire(hole_wire):
                hole_wire.set_parent(new_poly.outer_wire)
        return new_seg


    def _join_poly(self, segment):
        """
        Join polygons by removing a segment.
        """


        left_wire = segment.wire[left_side]
        right_wire = segment.wire[right_side]

        if left_wire.parent == right_wire.parent:
            assert left_wire == left_wire.polygon.outer_wire
            assert right_wire == right_wire.polygon.outer_wire
            orig_polygon = right_wire.polygon
            new_polygon = left_wire.polygon
            self.last_polygon_change = (PolygonChange.join, orig_polygon, new_polygon)
        else:
            if left_wire.parent == right_wire:
                # right is outer
                orig_polygon = right_wire.polygon
                new_polygon = left_wire.polygon
            else:
                assert right_wire.parent == left_wire
                # left is outer
                orig_polygon = left_wire.polygon
                new_polygon = right_wire.polygon
            self.last_polygon_change = (PolygonChange.remove, orig_polygon, new_polygon)

        # Join holes and free points
        for child in new_polygon.outer_wire.childs:
            child.set_parent(orig_polygon.outer_wire)

        for pt in new_polygon.free_points:
            pt.set_polygon(orig_polygon)

        # set parent for keeped wire
        right_wire.set_parent(orig_polygon.outer_wire)

        # fix wire links for
        for seg, side in left_wire.segments():
            assert seg.wire[side] == left_wire
            seg.wire[side] = right_wire

        segment.disconnect_vtx(out_vtx)
        segment.disconnect_vtx(in_vtx)
        segment.disconnect_wires()
        self._destroy_segment(segment)
        del self.wires[left_wire.id]
        del self.polygons[new_polygon.id]




    ###################################
    # Helper change operations.
    def _make_segment(self, points):
        seg = Segment(points)
        self.segments.append(seg)
        for vtx in [out_vtx, in_vtx]:
            seg.vtxs[vtx].join_segment(seg, vtx)
        self.pt_to_seg[ seg.vtxs_ids() ] = seg
        return seg

    def _destroy_segment(self, seg):
        seg.vtxs[out_vtx].rm_segment(seg, out_vtx)
        seg.vtxs[in_vtx].rm_segment(seg, in_vtx)
        a, b = seg.vtxs_ids()
        self.pt_to_seg.pop( (a, b), None )
        self.pt_to_seg.pop( (b, a), None)
        del self.segments[seg.id]


# Data classes contains no modification methods, all modifications are through reversible atomic operations.
class Point(IdObject):

    def __init__(self, point, poly):
        self.xy = np.array(point)
        self.poly = poly
        # Containing polygon for free-nodes. None for others.
        self.segment = (None, None)
        # (seg, vtx_side) One of segments joined to the Point and local idx of the segment (out_vtx, in_vtx).

    def __repr__(self):
        return "Pt({}) {}".format(self.id, self.xy)

    def is_free(self):
        """
        Indicator of a free point, not connected to eny segment.
        :return:
        """
        return self.segment[0] is  None

    def segments(self, start = (None, None) ):
        """
        Generator for segments joined to the point. Segments are yielded in the clock wise direction.
        :param :start = (segment, vtx_idx)
        yields: (segment, vtx_idx), where vtx_idx is index of 'point' in 'segment'
        """
        if start[0] is None:
            start = self.segment
        if start[0] is None:
            return
        seg_side = start
        while (1):
            yield seg_side
            seg, side = seg_side
            seg, other_side = seg.next[side]
            seg_side = seg, 1 - other_side
            if seg_side == start:
                return

    def insert_segment(self, vector):
        """
        Insert a vector between segments connected to the point.

        :param vector: (X, Y) ... any indexable pair.
        :return: ( (prev_seg, prev_side), (next_seg, next_side), wire )
        Previous segment side, and next segment side relative from inserted vector and the
        wire separated by the vector.
        """
        if self.segment[0] is None:
            return None
        vec_angle =  np.angle(complex(vector[0], vector[1]))
        last = (4*np.pi, None, None)
        self_segments = list(self.segments())
        self_segments.append(self.segment)
        for seg, vtx in  self_segments:
            seg_vec = seg.vector()
            if vtx == in_vtx:
                seg_vec *= -1.0
            angle = np.angle(complex(seg_vec[0], seg_vec[1]))
            da = angle - vec_angle
            if da < 0.0:
                da += 2*np.pi
            if da >= last[0]:
                prev = (last[1], last[2])
                next = (seg, 1 - vtx)
                break

            last = (da, seg, vtx)
        wire = prev[0].wire[prev[1]]
        # assert wire == next[0].wire[next[1]]
        return (prev, next, wire)



    def join_segment(self, seg, vtx):
        """
        Connect a segment side to the point.
        """
        if self.is_free():
            if self.poly is not None:
                del self.poly.free_points[self.id]
            self.poly = None
            self.segment = (seg, vtx)

    def rm_segment(self, seg, vtx):
        """
        Disconnect segment side.
        """
        assert seg.vtxs[vtx] == self
        for new_seg, side in self.segments():
            if not new_seg == seg:
                self.segment = (new_seg, side)
                return
        assert seg.is_dendrite()
        self.set_polygon(seg.wire[left_side].polygon)

    def set_polygon(self, polygon):
        if self.poly is not None:
            self.poly.free_points.pop(self.id)
        self.poly = polygon
        polygon.free_points[self.id] = self
        self.segment = (None, None)


    def colocated(self, xy_pt, tol):
        """
        Check if other point is close to  'self' point.
        :param xy_pt: Numpy array (X,Y)
        :param tol: Tolerance.
        :return: bool
        """
        return la.norm(self.xy - xy_pt) < tol

class Segment(IdObject):

    def __init__(self, vtxs):
        self.vtxs = list(vtxs)
        # tuple (out_vtx, in_vtx) of point objects; segment is oriented from out_vtx to in_vtx
        self.wire = [None, None]
        # (left_wire, right_wire) - wires on left and right side
        self.next = [None, None]
        # (left_next, right_next); next edge for left and right side;

    def __repr__(self):
        next = [ self._half_seg_repr(right_side), self._half_seg_repr(left_side) ]
        return "Seg({}) [ {}, {} ] next: {} wire: {}".format(self.id, self.vtxs[out_vtx], self.vtxs[in_vtx], next, self.wire )

    def _half_seg_repr(self, side):
        """
        Auxiliary method for __repr__.
        """
        if self.next[side] is None:
            return str(None)
        else:
            return (self.next[side][0].id, self.next[side][1])

    @staticmethod
    def side_to_vtx(side, side_vtx):
        tab = [ [in_vtx, out_vtx], [out_vtx, in_vtx]]
        return tab[side][side_vtx]


    def _set_next_side(self, side, next_seg):
        """
        Auxiliary method for connect_* methods.
        """
        assert next_seg[0].vtxs[1 - next_seg[1]] == self.vtxs[side]
        # prev vtx of next segment == next vtx of self segment
        self.next[side] = next_seg

    def connect_vtx(self, vtx_idx, insert_info):
        """
        Connect 'self' segment to a non-free point.
        :param vtx_idx: out_idx / in_idx; specification of the segment's endpoint to connect.
        :param insert_info: (prev_side, next_side, wire)
                ... as returned by Point.insert_segment and self.vtx_insert_info
        TODO: merge with connect_free_vtx ... common notation fo insert info.
        """
        self.vtxs[vtx_idx].join_segment(self, vtx_idx)
        prev, next, wire = insert_info
        set_side = vtx_idx
        self._set_next_side(set_side, next)

        prev_seg, prev_side = prev
        prev_seg._set_next_side(prev_side, (self, 1 - set_side) )
        self.wire[set_side] = wire
        #assert prev_seg.wire[prev_side] == wire    # this doesn't hold in middle of change operations

    def connect_free_vtx(self, vtx_idx, wire):
        """
        Connect 'self' segment to a free point.
        :param vtx_idx: out_idx / in_idx; specification of the segment's endpoint to connect.
        :param wire: Wire to set to the related side of the segment (in fact both sides should have same wire).
        """
        self.vtxs[vtx_idx].join_segment(self, vtx_idx)
        next_side = vtx_idx
        other_side = 1 - next_side
        self._set_next_side(next_side, (self, other_side))
        self.wire[next_side] = wire


    def vtx_insert_info(self, vtx_idx):
        """
        Return insert info for connecting after disconnect.
        """
        side_next = vtx_idx
        next = self.next[ side_next ]
        if next[0] == self:
            # veertex not conneected, i.e. dendrite tip
            return None
        wire = self.wire[ side_next ]

        side_prev = 1 - vtx_idx # prev side is next side of oposite vertex
        prev = self.previous(side_prev)
        return (prev, next, wire)


    def disconnect_vtx(self, vtx_idx):
        """
        Disconect next links of one vtx side of self segment.
        :param vtx_idx: out_vtx or in_vtx
        """
        self.vtxs[vtx_idx].rm_segment(self, vtx_idx)
        seg_side_prev = 1 - vtx_idx
        seg_side_next = vtx_idx

        prev_seg, prev_side = self.previous(seg_side_prev)
        prev_seg.next[prev_side] = self.next[seg_side_next]
        self.next[seg_side_next] = (self, seg_side_prev)


    def disconnect_wires(self):
        """
        Remove segment -> wire and wire ->segment links.
        """
        for side in [left_side, right_side]:
            wire = self.wire[side]
            if wire.segment == (self, side):
                wire.segment = self.next[side]
                assert wire.segment[0].wire[wire.segment[1]] == wire

    def contains_point(self, pt, tol):
        """
        Project point to segment line in X or Y direction and check if
        projection is close to the point in max norm.
        :param pt:
        :return:
        """
        Dxy = self.vector()
        axis = np.argmax(np.abs(Dxy))
        D = Dxy[axis]
        assert np.abs(D) > 1e-100
        t = (pt[axis] - self.vtxs[0].xy[axis]) / D
        t = min( max(t, 0.0), 1.0)
        xy = self.parametric(t)
        if la.norm(pt - xy, np.inf) < tol:
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
        eps = 1e-10
        if 0 <= t0 <= 1  and 0 + eps <= t1 <= 1 - eps:
            return (t0, t1)
        else:
            return (None, None)

    def x_line_isec(self, xy, tol = 1e-12):
        """
        Find intersection of the segment with a horizontal line passing through the given point.
        :param xy: The point. (X,Y) any indexable.
        :param tol: Tolerance. TODO: no default tolerance, pas in the tolerance of the Decomposition.
        :return: List of zero, one or two points. corresponding to no, point and segment intersections respectively.
        """
        vtxs = np.array([self.vtxs[out_vtx].xy, self.vtxs[in_vtx].xy])
        Dy = vtxs[1, 1] - vtxs[0, 1]
        magnitude = np.max(vtxs[:, 1])
        # require at least 4 decimal digit remaining precision of the Dy
        if np.abs(Dy) < tol:
            # horizontal edge
            min_y, max_y = np.sort(vtxs[:, 1])
            if min_y - tol <= xy[1] <= max_y + tol:
                return [ vtxs[0, 0], vtxs[1, 0] ]
            else:
                return []
        else:
            t = (xy[1] - vtxs[0, 1]) / Dy
            if 0 - tol < t < 1 + tol:
                Dx = vtxs[1, 0] - vtxs[0, 0]
                isec_x = t * Dx + vtxs[0, 0]
                return [isec_x]
            else:
                return []


    def is_on_x_line(self, xy):
        """
        Returns true if the segment is on the right horizontal halfline. startign in given point.
        TODO: Careful test of numerical stability when x_axis goes through
        a point or a segment is on it.
        :param xy:
        :return:
        """
        yy = [self.vtxs[out_vtx].xy[1], self.vtxs[in_vtx].xy[1]]

        if yy[0] < yy[1]:
            min_y, max_y = yy
        else:
            max_y, min_y = yy

        if min_y <= xy[1] < max_y:
            min_x = min([self.vtxs[out_vtx].xy[0], self.vtxs[in_vtx].xy[0]])
            if min_x > xy[0]:
                return True
        return False


    def vtxs_ids(self):
        return (self.vtxs[out_vtx].id, self.vtxs[in_vtx].id)


    def is_dendrite(self):
        return self.wire[left_side] == self.wire[right_side]

    def vector(self):
        return (self.vtxs[in_vtx].xy - self.vtxs[out_vtx].xy)

    def parametric(self, t):
        return  self.vector() * t + self.vtxs[out_vtx].xy

    def previous(self, side):
        """
        Oposite of seg.next[side]. Implemented through loop around a node.
        :param seg:
        :param side:
        :return: (previous segment, previous side), i.e. prev_seg.next[prev_side] == (self, side)
        """
        vtx_idx = Segment.side_to_vtx(side, 0)
        vtx = self.vtxs[vtx_idx]
        for seg, side in vtx.segments(start = (self, vtx_idx)):
            pass
        return (seg, side)

    def point_side(self, pt):
        if pt == self.vtxs[out_vtx]:
            return out_vtx
        elif pt == self.vtxs[in_vtx]:
            return in_vtx
        else:
            return None

class Wire(IdObject):

    def __init__(self):
        self.parent = self
        # Wire that contains this wire. None for the global outer boundary.
        # Parent relations are independent of polygons.
        self.childs=set()

        self.polygon = None
        # Polygon of this wire
        self.segment = (None, None)
        # One segment of the wire.

    def __eq__(self, other):
        # None is wire in infinity
        if self is None or other is None:
            return False
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __repr__(self):
        if self.is_root():
            return "Wire({}) root, poly: {}, childs: {}".\
            format(self.id, self.polygon.id, [ch.id for ch in self.childs])
        return "Wire({}) seg: {} poly: {} parent: {} childs: {}".\
            format(self.id, (self.segment[0].id, self.segment[1]),
                   self.polygon.id, self.parent.id, [ch.id for ch in self.childs])

    def repr_id(self):
        return self.id

    def is_root(self):
        return self.parent is None

    def set_parent(self, parent_wire):
        if self.parent is not None:
            assert self in self.parent.childs or self.parent == self
            self.parent.childs.discard(self)
        self.parent = parent_wire
        if parent_wire is not None:
            parent_wire.childs.add(self)


    def segments(self, start = (None, None), end = (None, None)):
        """
        Yields all (segmnet, side) of the same wire as the 'start' segment side,
        up to end segment side.
        """
        if start[0] is None:
            start = self.segment
        if end[0] is None:
            end = start

        seg_side = start
        visited = []
        while (1):
            visited.append( (seg_side[0], seg_side[1]) )
            yield seg_side
            segment, side = seg_side
            seg_side = segment.next[side]
            if seg_side == end:
                break
            if (seg_side[0], seg_side[1]) in visited:

                assert False, "Repeated seg: {}\nVisited: {}".format(seg_side, visited)
            assert not seg_side == start, "Inifinite loop."

    # def outer_segments(self):
    #     """
    #     :return: List of boundary componencts without tails. Single component is list of segments (with orientation)
    #     that forms outer boundary, i.e. excluding internal tails, i.e. segments appearing just once.
    #     TODO: This is not reliable for dendrites with holes. We should use whole wire for plotting.
    #     Then remove this method.
    #     """
    #     for seg, side  in self.segments():
    #         if not seg.is_dendrite():
    #             yield (seg, side)


    def contains_point(self, xy):
        """
        Check if the wire contains given point.
        TODO: use tolerance.
        :param xy:
        :return:
        """
        n_isec = 0
        for seg, side in self.segments():
            n_isec += int(seg.is_on_x_line(xy))
        if n_isec % 2 == 1:
            return True
        else:
            return False

    def contains_wire(self, wire):
        """
        Check if the 'self' wire contains other wire.
        Translates to call of 'contains_point' for carefully selected point.
        TODO: use tolerance.
        """
        if self.is_root():
            return True
        if wire.is_root():
            return False

        # test if a point of wire is inside 'self'
        seg, side = wire.segment
        tang = seg.vector()
        norm = tang[[1,0]]
        norm[0] = -norm[0]  # left side normal
        if side == right_side:
            norm = -norm
        eps = 1e-10     # TODO: review this value to be as close to the line as possible while keep intersection work
        inner_point = seg.vtxs[out_vtx].xy + 0.5 * tang  + eps * norm
        return self.contains_point(inner_point)

    def child_wires(self):
        """
        Yields all child wires recursively.
        :return:
        """
        for child in self.childs:
            yield child
            seg, side  = child.segment
            other_wire = seg.wire[1 - side]
            if not other_wire == child:
                yield other_wire
                yield from other_wire.child_wires()
                

class Polygon(IdObject):

    def __init__(self, outer_wire):
        self.outer_wire = outer_wire
        # outer boundary wire
        self.free_points = {}
        # Dict ID->pt of free points inside the polygon.


    def __repr__(self):
        outer = self.outer_wire.id
        return "Poly({}) out wire: {}".format(self.id, outer)

    def depth(self):
        """
        LAYERS
        Return depth of the polygon. That is number of other polygons it is contained in.
        :return: int
        """
        depth=0
        wire = self.outer_wire
        while (not wire.is_root()):
            depth += 1
            wire = wire.parent

    def vertices(self):
        """
        LAYERS
        Return list of polygon vertices (point objects) in counter clockwise direction.
        :return:
        """
        if self.outer_wire.is_root():
            return []
        return [seg.vtxs[side] for seg, side in self.outer_wire.segments()]


    def child_polygons(self):
        """
        Yield all child polygons, i.e. polygons inside the self.outer_wire.
        """
        yield self
        for wire in self.outer_wire.child_wires():
            if wire == wire.polygon.outer_wire:
                yield wire.polygon
