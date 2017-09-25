import numpy as np
import bisect


class PolygonDecomposition:
    """
    Decomposition of a plane into (non-convex) polygonal subsets (not necessarily domains).
    """

    def __init__(self):
        """
        Constructor.
        """
        self.points = {}
        # Points dictionary ID -> Point
        self.segments = {}
        # Segmants dictionary ID - > Segmant
        self.polygons = {}
        # Polygon dictionary ID -> Polygon
        self.polygons.append(Polygon(0, None, None))

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
        for e in self.edges:
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
            self._split_segment(obj, t)
        else:
            poly = t
            self._add_free_point(obj, point, poly)


    def add_line(self, a_vtx, b_vtx):
        """
        Try to add new line from point A to point B. Check intersection with any other line and
        call add_point for endpoints and intersections, then call operation connect_points for individual
        segments.
        :param a_vtx: numpy array X, Y
        :param b_vtx: numpy array X, Y
        :return:
        """
        a = np.array(a_vtx)
        b = np.array(b_vtx)
        t_list = []
        for e in self.edges:
            (t0, t1) = e.line_line(a, b)
            if t1 is not None:
                t_list.append( (t1, e) )
        t_list.sort()
        start_p = a
        dab = b - a
        for t, e in t_list:
            end_p = dab * t + a
            self._add_segment(start_p, end_p)
            start_p = end_p
        self._add_segment(start_p, b)


    # Reversible operations
    # Action ( forward, backward ),
    # forward = (add_free_point, X, Y)  ... func name, params
    # backward = (remove_free_point, pt_id) ... func name , params
    def _add_free_point(self, point, poly):
        """
        :param point: XY array
        :return: Point instance
        """
        id = self.points.size()
        self.points.append(Point(id, point, poly))


    def _remove_free_point(self, point):
        pass

    def _split_segment(self, seg, point):
        """
        Split a segment into two segments. Original keeps the start point.
        :param seg:
        :param t_point:
        :return:
        """
        id = self.points.size()
        mid_pt = Point(id, point, None)
        #mid_pt.segment =
        self.points.append(mid_pt)

        new_seg = Segment(id, (mid_pt, seg.points[1]), seg.polygon, seg.ori, (seg, seg), seg.next)
        seg.points[1] = mid_pt
        seg.next = (new_seg, new_seg)


    def _join_lines(self, point, lines):
        pass

    def _add_segment(self, a, b):
        pass

    def _remove_segment(self, a, b):
        pass

# Data classes contins no modification methods, all modifications are through reversible atomic operations.
class Point:
    def __init__(self, id, point, poly):
        self.id = id
        self.pt = point
        self.poly = poly
        #self.segment = None

class Segment:
    def __init__(self, id, points, polygon, ori, prev, next):
        self.id = id
        self.points = points
        # tuple (start, end) point object
        self.polygon = polygon
        # (left_poly, right_poly) - polygons on left and right side
        self.ori = ori
        # (left_ori, right_ori); indicator if segment orientation match ccwise direction of the polygon
        self.prev = prev
        # (left_prev, right_prev);  previous edge for left and right side;
        self.next = next
        # (left_next, right_next); next edge for left and right side;

    def contains_point(self, pt):
        Dxy = self.points[1] - self.points[0]
        axis = np.argmax(Dxy)
        D = Dxy[axis]
        magnitude = np.max(self.points[:, axis])
        assert np.abs(D) > 1e-12 * magnitude
        t = (pt[axis] - self.points[0, axis]) / D
        if 0 <= t <= 1:
            return t
        else:
            return None

class Polygon:
    def __init__(self, id, segment, ori):
        self.id = id
        self.segment = segment
        # First segment
        self.seg_ori = ori
        # Indicate if the oriantation of the first segment math ccwise direction.

