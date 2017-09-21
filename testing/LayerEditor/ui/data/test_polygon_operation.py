from ui.data.diagram_structures import Point, Line
from ui.data.polygon_operation import Polyline


class TestPolyline:
    def test_get_boundary_polyline(self):
        bp = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]
        bl = [Line(bp[0], bp[1]), Line(bp[1], bp[2]), Line(bp[2], bp[3]), Line(bp[3], bp[4]), Line(bp[4], bp[0])]

        poly = Polyline.get_boundary_polyline(bl, bp, bp[1], bp[3])
        # lines in first way
        assert poly.lines == bl[1:3]
        # points in first way
        assert poly.points == bp[1:4]

        poly = Polyline.get_boundary_polyline(bl, bp, bp[1], bp[3], True)
        # lines in revert way
        assert poly.lines == [bl[0], bl[4], bl[3]]
        # points in revert way
        assert poly.points == [bp[1], bp[0], bp[4], bp[3]]

    def test_split(self):
        p = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l = [Line(p[0], p[1]), Line(p[1], p[2])]

        a = Polyline()
        a.lines = l
        a.points = p
        b = a.split(p[1])

        # check splitted polylines
        assert a.lines == [l[0]]
        assert a.points == [p[0], p[1]]
        assert b.lines == [l[1]]
        assert b.points == [p[1], p[2]]

    def test_join(self):
        p1 = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l1 = [Line(p1[0], p1[1]), Line(p1[1], p1[2])]
        p2 = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l2 = [Line(p2[0], p2[1]), Line(p2[1], p2[2])]

        # 1. type
        a = Polyline()
        a.lines = l1.copy()
        a.points = p1.copy()

        b = Polyline()
        b.lines = l2.copy()
        b.points = p2.copy()

        b.points[0] = a.points[-1]
        nl = Line(b.points[0], b.points[1])
        b.lines[0] = nl

        a.join(b)
        # check joined polylines
        assert a.lines == l1 + [nl] + l2[1:]
        assert a.points == p1 + p2[1:]

        # 2. type
        a = Polyline()
        a.lines = l1.copy()
        a.points = p1.copy()

        b = Polyline()
        b.lines = l2.copy()
        b.points = p2.copy()

        b.points[-1] = a.points[-1]
        nl = Line(b.points[-2], b.points[-1])
        b.lines[-1] = nl

        a.join(b)
        # check joined polylines
        assert a.lines == l1 + [nl] + l2[-2::-1]
        assert a.points == p1 + p2[-2::-1]

        # 3. type
        a = Polyline()
        a.lines = l1.copy()
        a.points = p1.copy()

        b = Polyline()
        b.lines = l2.copy()
        b.points = p2.copy()

        b.points[0] = a.points[0]
        nl = Line(b.points[0], b.points[1])
        b.lines[0] = nl

        a.join(b)
        # check joined polylines
        assert a.lines == l1[::-1] + [nl] + l2[1:]
        assert a.points == p1[::-1] + p2[1:]

        # 4. type
        a = Polyline()
        a.lines = l1.copy()
        a.points = p1.copy()

        b = Polyline()
        b.lines = l2.copy()
        b.points = p2.copy()

        a.points[0] = b.points[-1]
        nl = Line(a.points[0], a.points[1])
        a.lines[0] = nl

        a.join(b)
        # check joined polylines
        assert a.lines == l2 + [nl] + l1[1:]
        assert a.points == p2 + p1[1:]

    def test_append(self):
        p = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l = [Line(p[0], p[1]), Line(p[1], p[2])]

        # 1. type
        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        np = Point(0, 0)
        nl = Line(a.points[-1], np)

        a.append(nl)
        # check append
        assert a.lines == l + [nl]
        assert a.points == p + [np]

        # 2. type
        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        np = Point(0, 0)
        nl = Line(np, a.points[-1])

        a.append(nl)
        # check append
        assert a.lines == l + [nl]
        assert a.points == p + [np]

        # 3. type
        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        np = Point(0, 0)
        nl = Line(a.points[0], np)

        a.append(nl)
        # check append
        assert a.lines == [nl] + l
        assert a.points == [np] + p

        # 4. type
        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        np = Point(0, 0)
        nl = Line(np, a.points[0])

        a.append(nl)
        # check append
        assert a.lines == [nl] + l
        assert a.points == [np] + p

    def test_second(self):
        p = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l = [Line(p[0], p[1]), Line(p[1], p[2])]

        a = Polyline()
        a.lines = l
        a.points = p

        # check second end point
        assert a.second(p[0]) == p[2]
        assert a.second(p[2]) == p[0]

    def test_remove_end(self):
        p = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]
        l = [Line(p[0], p[1]), Line(p[1], p[2]), Line(p[2], p[3])]

        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        a.remove_end(p[0])
        # check after remove
        assert a.lines == l[:-1]
        assert a.points == p[:-1]

        a.remove_end(p[-2])
        # check after remove
        assert a.lines == l[1:-1]
        assert a.points == p[1:-1]






# todo:
# PolygonGroups
# - vsechno necarkovany
# - _get_fake_path
# - add_inner_polygon - netestovat
#
# PolylineCluster
# - reduce_polylines
# - co maji spllit v nazvu
