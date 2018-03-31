import numpy as np
import numpy.linalg as la
import enum
import gm_base.polygons.aabb_lookup as aabb_lookup
import gm_base.polygons.decomp as decomp

from gm_base.polygons.decomp import PolygonChange

# TODO: rename point - > node
# TODO: careful unification of tolerance usage.
# TODO: Performance tests:
# - snap_point have potentialy very bad complexity O(Nlog(N)) with number of segments
# - add_line linear with number of segments
# - other operations are at most linear with number of segments per wire or point


in_vtx = left_side = 1
# vertex where edge comes in; side where next segment is connected through the in_vtx
out_vtx = right_side = 0
# vertex where edge comes out; side where next segment is connected through the out_vtx



class PolygonDecomposition:
    """
    Frontend to Decomposition.
    Provides high level operations.

    Methods that works with some tolerance:
    Segment:

      intersection - tolerance for snapping to the end points, fixed eps = 1e-10
                   - snapping only to one of intersectiong segments

      is_on_x_line - no tolerance, but not sure about numerical stability

    Wire:
        contains_point(self, xy):   called by Polygon.contains_point
            -> seg.is_on_x_line(xy)

        contains_wire(self, wire):
            - fixed tolerance eps=1e-10
            -> self.contains_point(inner_point)

    PD.snap_point, use slef. tolerance consistently

    """

    def __init__(self):
        """
        Constructor.
        """
        self.decomp = decomp.Decomposition()
        self.tolerance = 0.01


    def __repr__(self):
        stream = "PolygonDecomposition\n"
        stream+=str(self.decomp)
        return stream

    # def __eq__(self, other):
    #     return len(self.points) == len(other.points) \
    #         and len(self.segments) == len(other.segments) \
    #         and len(self.polygons) == len(other.polygons)

    @property
    def points(self):
        return self.decomp.points

    @property
    def segments(self):
        return self.decomp.segments

    @property
    def polygons(self):
        return self.decomp.polygons

    @property
    def outer_polygon(self):
        return self.decomp.outer_polygon

    ##################################################################
    # Interface for LayerEditor. Should be changed.
    ##################################################################
    def add_free_point(self, point_id, xy, polygon_id):
        """
        LAYERS
        :param point_id: ID of point to add.
        :param xy: point: (X,Y)
        :param polygon_id: Hit in which polygon place the point.
        :return: Point instance
        """

        #print("add_free_point", point_id, xy, polygon_id)
        polygon = self.decomp.polygons[polygon_id]
        assert polygon.contains_point(xy), "Point {} not in polygon: {}.\n{}".format(xy, polygon, self)
        return self.decomp._add_free_point(xy, polygon, id = point_id)


    def remove_free_point(self, point_id):
        """
        LAYERS
        :param: point_id - ID of free point to remove
        :return: None
        """
        point = self.decomp.points[point_id]
        self.decomp._remove_free_point(point)
 
    def new_segment(self, a_pt, b_pt):
        """
        LAYERS
        Add segment between given existing points. Assumes that there is no intersection with other segment.
        Just return the segment if it exists.
        :param a_pt: Start point of the segment.
        :param b_pt: End point.
        :return: new segment
        """
        return self.decomp.new_segment(a_pt, b_pt)


    def delete_segment(self, segment):
        """
        LAYERS
        Remove specified segment.
        :param segment:
        :return: None
        """
        return self.decomp.delete_segment(segment)


    def check_displacment(self, points, displacement, margin):
        """
        LAYERS
        param: points: List of Points to move.
        param: displacement: Numpy array, 2D vector of displacement to add to the points.
        param: margin: float between (0, 1), displacement margin as a fraction of maximal displacement
        TODO: Check fails for internal wires and nonconvex poygons.
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
                (t0, t1) = self.seg_intersection(seg, pt.xy, pt.xy + new_displ)
                # TODO: Treat case of vector and segment in line.
                # TODO: Check bound checks in intersection.
                if t0 is not None:
                    new_displ *= (1.0 - margin) * t1
        self.decomp.last_polygon_change = (decomp.PolygonChange.shape, changed_polygons, None)
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
        (PolygonChange.join, orig_poly_id, del_poly_id) - join both polygons into orig_poly

        After init of PolygonDecomposition this method returns:
        (PolygonChange.add, outer_polygon_id, outer_polygon_id)
        """
        type, p0, p1 = self.decomp.last_polygon_change
        if type == decomp.PolygonChange.shape:
            poly_ids = [poly.id for poly in p0]
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
        # TODO: remove after problem with infinite recursion is solved
        for w in self.decomp.wires.values():
            w._get_child_passed = False

        #print(self)
        child_poly_id_set = set()
        root_poly = self.decomp.polygons[polygon_id]
        for poly in  root_poly.child_polygons():
            child_poly_id_set.add(poly.id)
        return child_poly_id_set

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






    ###################################################################
    # Macro operations that change state of the decomposition.
    def add_point(self, point):
        """
        Try to add a new point, snap to lines and existing points.
        :param point: numpy array with XY coordinates
        :return: Point instance.

        This operation translates to atomic operations: add_free_point and split_line_by_point.
        TODO: make consisten system to check ide effects of decomp operations.
        This is partly done with get_last_polygon_changes but we need similar for segment in this method.
        This is necessary in intersections.
        """
        point = np.array(point, dtype=float)
        dim, obj, t = self._snap_point(point)
        if dim == 0:
            # nothing to add
            return obj
        elif dim == 1:
            # TODO: check if this could happen after _snap_ppoint
            if t < self.tolerance:
                return obj.vtxs[out_vtx]
            elif t > 1.0 - self.tolerance:
                return obj.vtxs[in_vtx]

            return self.decomp._split_segment(obj, t)
        else:
            poly = obj
            return self.decomp._add_free_point(point, poly)


    def _snap_point(self, point):
        """
        Find object (point, segment, polygon) within tolerance from given point.
        :param point: numpy array X, Y
        :return: (dim, obj, param) Where dim is object dimension (0, 1, 2), obj is the object (Point, Segment, Polygon).
        'param' is:
          Point: None
          Segment: parameter 't' of snapped point on the segment
          Polygon: None
        """
        point = np.array(point, dtype=float)

        # First snap to points
        for pt in self.decomp.points.values():
            if la.norm(pt.xy - point) <  self.tolerance:
                return (0, pt, None)

        # Snap to segments, keep the closest to get polygon.
        closest_seg = (np.inf, None, None)
        for seg in self.decomp.segments.values():
            t = self.seg_project_point(seg, point)
            dist = la.norm(point - seg.parametric(t))
            if dist < self.tolerance:
                return (1, seg, t)
            elif dist < closest_seg[0]:
                closest_seg = (dist, seg, t)

        # Snap to polygon,
        # have to deal with nonconvex case
        poly = None
        dist, seg, t = closest_seg
        if seg is None:
            return (2, self.decomp.outer_polygon, None)
        if t == 0.0:
            pt = seg.vtxs[out_vtx]
        elif t == 1.0:
            pt = seg.vtxs[in_vtx]
        else:
            # convex case
            tangent = seg.vector()
            normal = np.array([tangent[1], -tangent[0]])
            point_n = (point - seg.vtxs[out_vtx].xy).dot(normal)
            assert point_n != 0.0
            if  point_n > 0:
                poly = seg.wire[right_side].polygon
            else:
                poly = seg.wire[left_side].polygon

        if poly is None:
            # non-convex case
            prev, next, wire = pt.insert_vector(point - pt.xy)
            poly = wire.polygon
        if not poly.contains_point(point):
            assert False
        return (2, poly, None)


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
        if a_point == b_point:
            return a_point
        return self.add_line_for_points(a_point, b_point)


    def add_line_for_points(self, a_pt, b_pt):
        """
        Same as add_line, but for known end points.
        :param a_pt:
        :param b_pt:
        :return:
        """
        line_div = self._add_line_seg_intersections(a_pt, b_pt)
        return [seg    for seg, change, side in self._add_line_new_segments(a_pt, b_pt, line_div)]

    def _add_line_seg_intersections(self, a_pt, b_pt):
        """
        Generator for intersections of a new line with existing segments.
        Every segment is split and intersection point is yield.
        :param a_pt, b_pt: End points of the new line.
        :returns a dictionary t -> (isec_pt, seg0, seg1),
            - parameter of the intersection on the new line
            - the Point object of the intersection point.
            - old and new subsegments of the segment split
            - new seg == old seg if point is snapped to the vertex
        """
        line_division = {}
        segments = list(self.decomp.segments.values()) # need copy since we change self.segments
        for seg in segments:
            (t0, t1) = self.seg_intersection(seg, a_pt.xy, b_pt.xy)
            if t1 is not None:
                if t0 < self.tolerance:
                    mid_pt =  seg.vtxs[out_vtx]
                    next_seg = seg
                elif t0 > 1.0 - self.tolerance:
                    mid_pt = seg.vtxs[in_vtx]
                    next_seg = seg
                else:
                    mid_pt = self.decomp._split_segment(seg, t0)
                    next_seg = seg.next[in_vtx][0]
                line_division[t1] = (mid_pt, seg, next_seg)
        return line_division

    def _add_line_new_segments(self, a_pt, b_pt, line_div):
        """
        Generator for added new segments of the new line.
        """
        start_pt = a_pt
        for t1, (mid_pt, seg0, seg1) in sorted(line_div.items()):
            if start_pt == mid_pt:
                continue
            new_seg = self.decomp.new_segment(start_pt, mid_pt)
            if type(new_seg) == decomp.Point:
                assert False
            yield (new_seg, self.decomp.last_polygon_change, new_seg.vtxs[out_vtx] == start_pt)
            start_pt = mid_pt
        new_seg = self.decomp.new_segment(start_pt, b_pt)
        yield (new_seg, self.decomp.last_polygon_change, new_seg.vtxs[out_vtx] == start_pt)

    # def _split_segment(self, seg, t_point):
    #     """
    #     Split a segment into two segments. Original keeps the start point.
    #     :param seg:
    #     :param t_point:
    #     :return:
    #     TODO: use common interface of Decomposition.
    #     """
    #     if t_point < self.tolerance:
    #         return seg.vtxs[out_vtx]
    #     elif t_point > 1.0 - self.tolerance:
    #         return seg.vtxs[in_vtx]
    #
    #
    #     xy_point = seg.parametric(t_point)
    #     mid_pt = Point(xy_point, None)
    #     self.decomp.points.append(mid_pt)
    #
    #     b_seg_insert = seg.vtx_insert_info(in_vtx)
    #     # TODO: remove this hard wired insert info setup
    #     # modify point insert method to return full insert info
    #     # it should have treatment of the single segment pint , i.e. tip
    #     seg_tip_insert = ( (seg, left_side), (seg, right_side), seg.wire[right_side])
    #     seg.disconnect_vtx(in_vtx)
    #     del self.decomp.pt_to_seg[tuple(id_list(seg.vtxs))]
    #     self.decomp.pt_to_seg[(seg.vtxs[0].id, mid_pt.id)] = seg
    #
    #     new_seg = self.decomp._make_segment((mid_pt, seg.vtxs[in_vtx]))
    #     seg.vtxs[in_vtx] = mid_pt
    #     new_seg.connect_vtx(out_vtx, seg_tip_insert)
    #     if b_seg_insert is None:
    #         assert seg.is_dendrite()
    #         new_seg.connect_free_vtx(in_vtx, seg.wire[left_side])
    #     else:
    #         new_seg.connect_vtx(in_vtx, b_seg_insert)
    #
    #     return mid_pt







    def delete_point(self, point):
        """
        Delete given point with all connected segments.
        :param point:
        :return:
        """
        segs_to_del = [ seg for seg, side in point.segments()]
        for seg in segs_to_del:
            self.delete_segment(seg)
        self.decomp._remove_free_point(point)


    def make_segment(self, node_ids):
        """
        Used in deep_copy and deserialize.

        :param node_ids:
        :return:
        """
        v_out_id, v_in_id = node_ids
        vtxs = (self.decomp.points[v_out_id], self.decomp.points[v_in_id])
        return self.decomp._make_segment(vtxs)

    def make_wire_from_segments(self, seg_ids, polygon):
        """
        Used in  deserialize.

        Set half segments of the wire, and the wire itself.
        :param seg_ids: Segment ids, at least 2 and listed in the orientation matching the wire (cc wise)
        :param polygon: Polygon the wire is part of.
        :return: None
        """
        assert len(seg_ids) >= 2, "segments: {}".format(seg_ids)
        wire = decomp.Wire()
        self.decomp.wires.append(wire)

        # detect orientation of the first segment
        last_seg = self.decomp.segments[seg_ids[0]]
        seg1 = self.decomp.segments[seg_ids[1]]
        last_side = out_vtx
        vtx0_side = seg1.point_side(last_seg.vtxs[last_side])
        if vtx0_side is None:
            last_side = in_vtx
            assert seg1.point_side(last_seg.vtxs[last_side]) is not None, "Can not connect segments: {} {}".format(last_seg, seg1)
        start_seg_side = (last_seg, last_side)

        # set segment sides along the wire
        for id in seg_ids[1:]:
            seg = self.decomp.segments[id]
            side = seg.point_side(last_seg.vtxs[last_side])
            assert side is not None, "Can not connect segments: {} {}".format(last_seg, seg)
            seg_side = (seg, 1 - side)
            last_seg.next[last_side] = seg_side
            last_seg.wire[last_side] = wire
            last_seg, last_side = seg_side
        last_seg.next[last_side] = start_seg_side
        last_seg.wire[last_side] = wire
        wire.segment = start_seg_side
        wire.polygon = polygon
        return wire

    def make_polygon(self, outer_segments, holes, free_points):
        """
        Used in  deep_copy and deserialize.

        :param outer_segments:
        :param holes:
        :param free_points:
        :return:
        """
        if len(outer_segments) != 0:
            p = self.decomp.polygons.append(decomp.Polygon(None))
            p.outer_wire = self.make_wire_from_segments(outer_segments, p)
        else:
            p = self.decomp.outer_polygon

        for hole in holes:
            wire = self.make_wire_from_segments(hole, p)
            wire.set_parent(p.outer_wire)
        for free_pt_id in free_points:
            pt = self.decomp.points[free_pt_id]
            pt.set_polygon(p)
        return p



    def set_wire_parents(self):
        """
        Used in  deep_copy and deserialize.

        Set parent wire links from holes.
        """
        for poly in self.decomp.polygons.values():
            for hole in poly.outer_wire.childs:
                child_queue = hole.neighbors()
                # BFS for inner wires of the hole
                while child_queue:
                    inner_wire = child_queue.pop(0)
                    if inner_wire.parent == inner_wire:
                        inner_wire.set_parent(hole)
                        for wire in inner_wire.neighbors():
                            child_queue.append(wire)



    # # Reversible atomic change operations.
    # # TODO: Add history notifiers to the return point.
    #
    # def _add_free_point(self, point, poly, id=None):
    #     """
    #     :param point: XY array
    #     :return: Point instance
    #     """
    #
    #     pt = Point(point, poly)
    #     if id is None:
    #         self.points.append(pt)
    #     else:
    #         self.points.append(pt, id)
    #     poly.free_points.add(pt)
    #     return pt
    #
    #
    # def _remove_free_point(self, point):
    #     assert point.poly is not None
    #     assert point.segment[0] is None
    #     point.poly.free_points.remove(point)
    #     del self.points[point.id]
    #
    #
    #
    #
    # def _join_segments(self, mid_point, seg0, seg1):
    #     """
    #     TODO: replace by del_segment and 2x new_segment
    #     """
    #     if seg0.vtxs[in_vtx] == mid_point:
    #         seg0_out_vtx, seg0_in_vtx = out_vtx, in_vtx
    #     else:
    #         seg0_out_vtx, seg0_in_vtx = in_vtx, out_vtx
    #
    #     if seg1.vtxs[out_vtx] == mid_point:
    #         seg1_out_vtx, seg1_in_vtx = out_vtx, in_vtx
    #     else:
    #         seg1_out_vtx, seg1_in_vtx = in_vtx, out_vtx
    #
    #     # Assert that no other segments are joined to the mid_point
    #     assert seg0.next[seg0_in_vtx] == (seg1, seg1_in_vtx)
    #     assert seg1.next[seg1_out_vtx] == (seg0, seg0_out_vtx)
    #
    #     b_seg1_insert = seg1.vtx_insert_info(seg1_in_vtx)
    #     seg1.disconnect_vtx(seg1_in_vtx)
    #     seg1.disconnect_vtx(seg1_out_vtx)
    #     seg0.disconnect_vtx(seg0_in_vtx)
    #     seg0.vtxs[seg0_in_vtx] = seg1.vtxs[seg1_in_vtx]
    #     if b_seg1_insert is None:
    #         assert seg0.is_dendrite()
    #         seg0.connect_free_vtx(seg0_in_vtx, seg0.wire[out_vtx])
    #     else:
    #         seg0.connect_vtx(seg0_in_vtx, b_seg1_insert)
    #
    #     # fix possible wire references
    #     for side in [left_side, right_side]:
    #         wire = seg1.wire[side]
    #         if wire.segment == (seg1, side):
    #             wire.segment = (seg0, side)
    #
    #     self._destroy_segment(seg1)
    #     self._remove_free_point(mid_point)
    #
    # def _new_wire(self, polygon, a_pt, b_pt):
    #     """
    #     New wire containing just single segment.
    #     return the new_segment
    #     """
    #
    #     wire = self.wires.append(Wire())
    #     wire.polygon = polygon
    #     wire.set_parent(polygon.outer_wire)
    #     seg = self._make_segment((a_pt, b_pt))
    #     seg.connect_free_vtx(out_vtx, wire)
    #     seg.connect_free_vtx(in_vtx, wire)
    #     wire.segment = (seg, right_side)
    #     return seg
    #
    # def _rm_wire(self, segment):
    #     """
    #     Remove the last segment of a wire.
    #     :return: None
    #     """
    #     assert segment.next[left_side] == (segment, right_side) and segment.next[right_side] == (segment, left_side)
    #     assert segment.is_dendrite()
    #     wire = segment.wire[left_side]
    #     polygon = wire.polygon
    #     polygon.outer_wire.childs.remove(wire)
    #     del self.wires[wire.id]
    #     self._destroy_segment(segment)
    #
    #
    # def _wire_add_dendrite(self, points, r_insert, root_idx):
    #     """
    #     Add new dendrite tip segment.
    #     points: (out_pt, in_pt)
    #     r_insert: insert information for root point
    #     root_idx: index (0/1) of the root, i.e. non-free point.
    #     """
    #     free_pt = points[1-root_idx]
    #     polygon = free_pt.poly
    #     r_prev, r_next, wire = r_insert
    #     assert wire.polygon == free_pt.poly, "point poly: {} insert: {}".format(free_pt.poly, r_insert)
    #
    #     seg = self._make_segment( points)
    #     seg.connect_vtx(root_idx, r_insert)
    #     seg.connect_free_vtx(1-root_idx, wire)
    #     self.last_polygon_change = (PolygonChange.shape, [polygon], None)
    #     return seg
    #
    # def _wire_rm_dendrite(self, segment, tip_vtx):
    #     """
    #     Remove dendrite tip segment.
    #     """
    #
    #     root_vtx = 1 - tip_vtx
    #     assert segment.is_dendrite()
    #     polygon = segment.wire[out_vtx].polygon
    #     segment.disconnect_wires()
    #     segment.disconnect_vtx(root_vtx)
    #
    #     self._destroy_segment(segment)
    #     self.last_polygon_change = (PolygonChange.shape, [polygon], None)
    #
    # def _join_wires(self, a_pt, b_pt, a_insert, b_insert):
    #     """
    #     Join two wires of the same polygon by new segment.
    #     """
    #     a_prev, a_next, a_wire = a_insert
    #     b_prev, b_next, b_wire = b_insert
    #     assert a_wire != b_wire
    #     assert a_wire.polygon == b_wire.polygon
    #     polygon = a_wire.polygon
    #     self.last_polygon_change = (PolygonChange.shape, [polygon], None)
    #
    #     # set next links
    #     new_seg = self._make_segment( (a_pt, b_pt))
    #     new_seg.connect_vtx(out_vtx, a_insert)
    #     new_seg.connect_vtx(in_vtx, b_insert)
    #
    #
    #     ############################
    #     keep_wire_side = None
    #     if polygon.outer_wire == a_wire:
    #         keep_wire_side = out_vtx # a_wire
    #     elif polygon.outer_wire == b_wire:
    #         keep_wire_side = in_vtx  # b_wire
    #
    #
    #     if keep_wire_side is None:
    #         # connect two holes
    #         keep_wire_side = in_vtx
    #         keep_wire = new_seg.wire[keep_wire_side]
    #         rm_wire = new_seg.wire[ 1 - keep_wire_side]
    #         parent_wire = keep_wire
    #     else:
    #         keep_wire = new_seg.wire[keep_wire_side]
    #         rm_wire = new_seg.wire[ 1 - keep_wire_side]
    #         parent_wire = keep_wire.parent  # parent wire to set for childs of rm_wire
    #         polygon.outer_wire = keep_wire
    #
    #     # update segment links to rm_wire
    #     for seg, side in rm_wire.segments(start= (new_seg, 1 - keep_wire_side), end= (new_seg, keep_wire_side)):
    #         assert seg.wire[side] == rm_wire, "wire: {} bwire: {} awire{}".format(seg.wire[side], b_wire, a_wire)
    #         seg.wire[side] = keep_wire
    #     new_seg.wire[out_vtx] = keep_wire
    #
    #     # update child links to rm_wire
    #     for child in list(rm_wire.childs):
    #          child.set_parent(parent_wire)
    #
    #     # update parent link to rm_wire
    #     rm_wire.parent.childs.remove(rm_wire)
    #     #####################
    #     del self.wires[rm_wire.id]
    #
    #     return new_seg
    #
    #
    # def _split_wire(self, segment):
    #     """
    #     Remove segment that connects two wires.
    #     """
    #     """
    #      Remove segment that connects two wires.
    #      """
    #     assert segment.is_dendrite()
    #     a_wire = segment.wire[left_side]
    #     polygon = a_wire.polygon
    #     b_wire = self.wires.append(Wire())
    #
    #     # set new wire to segments (b_wire is on the segment side of the vtx[1])
    #     b_vtx_next_side = in_vtx
    #     b_vtx_prev_side = 1 - b_vtx_next_side
    #     b_next_seg = segment.next[b_vtx_next_side]
    #     for seg, side in a_wire.segments(start = b_next_seg, end = (segment, b_vtx_prev_side)):
    #         assert seg.wire[side] == a_wire
    #         seg.wire[side] = b_wire
    #
    #     segment.disconnect_wires()
    #     segment.disconnect_vtx(out_vtx)
    #     segment.disconnect_vtx(in_vtx)
    #
    #
    #     # setup new b_wire
    #     b_wire.segment = b_next_seg
    #     b_wire.polygon = a_wire.polygon
    #     if polygon.outer_wire == a_wire:
    #         # one wire inside other
    #         outer_wire, inner_wire = b_wire, a_wire
    #         if a_wire.contains_wire(b_wire):
    #             outer_wire, inner_wire = a_wire, b_wire
    #         polygon.outer_wire = outer_wire
    #         outer_wire.set_parent(a_wire.parent)  # outer keep parent of original wire
    #         inner_wire.set_parent(outer_wire)
    #         self._update_wire_parents(a_wire.parent, a_wire.parent, inner_wire)
    #
    #     else:
    #         # both wires are holes
    #         b_wire.set_parent(a_wire.parent)
    #         self._update_wire_parents(a_wire, a_wire, b_wire)
    #
    #     # remove segment
    #     self.last_polygon_change = (PolygonChange.shape, [polygon], None)
    #     self._destroy_segment(segment)
    #
    # def _update_wire_parents(self, orig_wire, outer_wire, inner_wire):
    #     # Auxiliary method of _split_wires.
    #     # update all wires having orig wire as parent
    #     # TODO: use wire childs
    #     for wire in self.wires.values():
    #         if wire.parent == orig_wire:
    #             if inner_wire.contains_wire(wire):
    #                 wire.set_parent(inner_wire)
    #             else:
    #                 wire.set_parent(outer_wire)
    #
    #
    # def _split_poly(self, a_pt, b_pt, a_insert, b_insert):
    #     """
    #     Split polygon by new segment.
    #     """
    #     a_prev, a_next, a_wire = a_insert
    #     b_prev, b_next, b_wire = b_insert
    #     assert a_wire == b_wire
    #     orig_wire  = a_wire
    #
    #     right_wire = a_wire
    #     left_wire = self.wires.append(Wire())
    #
    #     # set next links
    #     new_seg = self._make_segment( (a_pt, b_pt))
    #     new_seg.connect_vtx(out_vtx, a_insert)
    #     new_seg.connect_vtx(in_vtx, (b_prev, b_next, left_wire))
    #
    #     # set right_wire links
    #     for seg, side in orig_wire.segments(start=new_seg.next[left_side], end = (new_seg, left_side)):
    #         assert seg.wire[side] == orig_wire
    #         seg.wire[side] = left_wire
    #     left_wire.segment = (new_seg, left_side)
    #     right_wire.segment = (new_seg, right_side)
    #
    #     # update polygons
    #     orig_poly = right_poly = orig_wire.polygon
    #     new_poly = Polygon(left_wire)
    #     self.polygons.append(new_poly)
    #     left_wire.polygon = new_poly
    #
    #     if orig_wire.polygon.outer_wire == orig_wire:
    #         # two disjoint polygons
    #         new_poly.outer_wire = left_wire
    #         left_wire.set_parent( orig_wire.parent)
    #         self.last_polygon_change = (PolygonChange.split, orig_poly, new_poly)
    #     else:
    #         assert orig_wire.parent == orig_poly.outer_wire
    #         # two embedded wires/polygons
    #         if right_wire.contains_wire(left_wire):
    #             inner_wire, outer_wire = left_wire, right_wire
    #         else:
    #             inner_wire, outer_wire = right_wire, left_wire
    #
    #         # fix childs of orig_wire
    #         for child in list(orig_wire.childs):
    #             child.set_parent(outer_wire)
    #
    #         outer_wire.polygon = orig_poly
    #         inner_wire.polygon = new_poly
    #         new_poly.outer_wire = inner_wire
    #         outer_wire.set_parent( orig_wire.parent)
    #         inner_wire.set_parent( outer_wire )
    #         self.last_polygon_change = (PolygonChange.add, orig_poly, new_poly)
    #
    #     # split free points
    #     for pt in list(orig_poly.free_points):
    #         if new_poly.outer_wire.contains_point(pt.xy):
    #             pt.set_polygon(new_poly)
    #
    #     # split holes
    #     for hole_wire in list(orig_poly.outer_wire.childs):
    #         if new_poly.outer_wire.contains_wire(hole_wire):
    #             hole_wire.set_parent(new_poly.outer_wire)
    #             hole_wire.polygon = new_poly
    #     return new_seg
    #
    #
    # def _join_poly(self, segment):
    #     """
    #     Join polygons by removing a segment.
    #     """
    #
    #
    #     left_wire = segment.wire[left_side]
    #     right_wire = segment.wire[right_side]
    #
    #     if left_wire.parent == right_wire.parent:
    #         assert left_wire == left_wire.polygon.outer_wire
    #         assert right_wire == right_wire.polygon.outer_wire
    #         orig_polygon = right_wire.polygon
    #         new_polygon = left_wire.polygon
    #         self.last_polygon_change = (PolygonChange.join, orig_polygon, new_polygon)
    #         keep_wire = right_wire
    #     else:
    #         if left_wire.parent == right_wire:
    #             # right is outer
    #             orig_polygon = right_wire.polygon
    #             new_polygon = left_wire.polygon
    #             keep_wire = right_wire
    #         else:
    #             assert right_wire.parent == left_wire
    #             # left is outer
    #             orig_polygon = left_wire.polygon
    #             new_polygon = right_wire.polygon
    #             keep_wire = left_wire
    #         self.last_polygon_change = (PolygonChange.remove, orig_polygon, new_polygon)
    #
    #     rm_wire = new_polygon.outer_wire
    #
    #     # Join holes and free points
    #     for child in list(rm_wire.childs):
    #         child.set_parent(keep_wire)
    #
    #     for pt in list(new_polygon.free_points):
    #         pt.set_polygon(orig_polygon)
    #
    #     # set parent for keeped wire
    #     #right_wire.set_parent(orig_polygon.outer_wire)
    #
    #     rm_wire.set_parent(rm_wire) # disconnect
    #
    #     # fix wire links for
    #     for seg, side in rm_wire.segments():
    #         assert seg.wire[side] == rm_wire
    #         seg.wire[side] = keep_wire
    #
    #     segment.disconnect_wires()
    #     segment.disconnect_vtx(out_vtx)
    #     segment.disconnect_vtx(in_vtx)
    #
    #     self._destroy_segment(segment)
    #     del self.wires[rm_wire.id]
    #     del self.polygons[new_polygon.id]


    ###################################
    # Helper change operations.
    # def _make_segment(self, points):
    #     seg = Segment(points)
    #     if points[0] == points[1]:
    #         assert False
    #     self.segments.append(seg)
    #     for vtx in [out_vtx, in_vtx]:
    #         seg.vtxs[vtx].join_segment(seg, vtx)
    #     self.pt_to_seg[ seg.vtxs_ids() ] = seg
    #     return seg
    #
    # def _destroy_segment(self, seg):
    #     seg.vtxs[out_vtx].rm_segment(seg, out_vtx)
    #     seg.vtxs[in_vtx].rm_segment(seg, in_vtx)
    #     a, b = seg.vtxs_ids()
    #     self.pt_to_seg.pop( (a, b), None )
    #     self.pt_to_seg.pop( (b, a), None)
    #     del self.segments[seg.id]

    @staticmethod
    def seg_project_point(seg, pt):
        """
        Return parameter t of the projection to the segment.
        :param pt: numpy [X,Y]
        :return: t
        """
        Dxy = seg.vector()
        AX = pt - seg.vtxs[out_vtx].xy
        dxy2 = Dxy.dot(Dxy)
        assert dxy2 != 0.0
        t = AX.dot(Dxy)/dxy2
        return min(max(t, 0.0), 1.0)


    @staticmethod
    def seg_intersection(seg, a, b):
        """
        Find intersection of 'self' and (a,b) edges.
        :param a: start vtx of edge1
        :param b: end vtx of edge1
        :return: (t0, t1) Parameters of the intersection for 'self' and other edge.
        """
        mat = np.array([ seg.vector(), a - b])
        rhs = a - seg.vtxs[0].xy
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


