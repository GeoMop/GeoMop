from ui.data.diagram_structures import Point, Line
from ui.data.polygon_operation import Polyline, PolylineCluster


def create_polyline(p1, p2, num_lines=2):
    """
    Create polyline from p1 to p2 with num_lines lines.
    :param p1: first point
    :param p2: second point
    :param num_lines: number of lines
    :return: created polyline
    """
    p = [p1]
    l = []
    for i in range(num_lines - 1):
        p.append(Point(0, 0))
        l.append(Line(p[i], p[i + 1]))
        p[i].lines.append(l)
        p[i+1].lines.append(l)        
    p.append(p2)
    l.append(Line(p[-2], p[-1]))
    p[-2].lines.append(l)
    p[-1].lines.append(l)

    poly = Polyline()
    poly.lines = l
    poly.points = p
    return poly


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
        assert a.lines == l[1:]
        assert a.points == p[1:]

        a.remove_end(p[-1])
        # check after remove
        assert a.lines == l[1:-1]
        assert a.points == p[1:-1]


class TestPolygonGroups:
    def test_move(self):
        pass

    def test_refresh_polygon(self):
        pass

    def test_add_polygon(self):
        pass

    def test_get_boundary_polyline(self):
        pass

    def test_get_fake_path(self):
        pass

    def test_del_polygon(self):
        pass


class TestPolylineCluster:
    def test_reduce_polylines(self):
        # bundles
        a = Point(0, 0)
        b = Point(0, 0)
        c = Point(0, 0)
        d = Point(0, 0)
        e = Point(0, 0)

        # joins
        join = Point(0, 0)
        inner_join = Point(0, 0)

        # construct cluster
        cluster = PolylineCluster()
        cluster.polylines = [create_polyline(a, b),
                             create_polyline(b, c),
                             create_polyline(c, a),
                             create_polyline(a, d),
                             create_polyline(b, e),
                             create_polyline(e, Point(0, 0)),
                             create_polyline(a, inner_join),
                             create_polyline(c, join)]
        cluster.bundles = [a, b, c, d, e]
        cluster.joins = [join]
        cluster.inner_joins = [inner_join]

        res = cluster.reduce_polylines()
        # check reduction
        assert res == cluster.polylines[:3] + cluster.polylines[-2:]

    def test_split_cluster(self):
        # 1. case
        # \   /
        #  -x-
        # /   \
        #########
        # bundles
        a = Point(0, 0)
        b = Point(0, 0)

        polylines = [create_polyline(a, b, 3),
                     create_polyline(Point(0, 0), a),
                     create_polyline(Point(0, 0), a),
                     create_polyline(b, Point(0, 0)),
                     create_polyline(b, Point(0, 0))]
                     
        # test polyline joins
        assert len(a.lines)==3
        assert len(b.lines)==3

        # construct cluster
        cluster = PolylineCluster()
        cluster.polylines = polylines.copy()
        cluster.bundles = [a, b]

        line = polylines[0].lines[1]
        new_cluster = cluster.split_cluster(line)
        # check split
        assert cluster.polylines == polylines[:3]
        assert len(cluster.polylines[0].lines) == 1
        assert cluster.bundles == [a]
        assert len(new_cluster.polylines) == 3
        assert len(new_cluster.polylines[0].lines) == 1
        assert new_cluster.polylines[1:] == polylines[-2:]
        assert new_cluster.bundles == [b]

    # 2. case
    # \  /
    #  -x
    # /  \
    #########
    # bundles
    a = Point(0, 0)
    b = Point(0, 0)

    polylines = [create_polyline(a, b, 2),
                 create_polyline(Point(0, 0), a),
                 create_polyline(Point(0, 0), a),
                 create_polyline(b, Point(0, 0)),
                 create_polyline(b, Point(0, 0))]

    # test polyline joins
    assert len(a.lines) == 3
    assert len(b.lines) == 3

    # construct cluster
    cluster = PolylineCluster()
    cluster.polylines = polylines.copy()
    cluster.bundles = [a, b]

    line = polylines[0].lines[1]
    new_cluster = cluster.split_cluster(line)
    # check split
    assert cluster.polylines == polylines[:3]
    assert len(cluster.polylines[0].lines) == 1
    assert cluster.bundles == [a]
    assert len(new_cluster.polylines) == 1
    assert len(new_cluster.polylines[0].lines) == 4
    assert len(new_cluster.bundles) == 0

    # 3. case
    # \  /
    #  -x-
    # /  \
    #########
    # bundles
    a = Point(0, 0)
    b = Point(0, 0)

    polylines = [create_polyline(a, b, 2),
                 create_polyline(Point(0, 0), a),
                 create_polyline(Point(0, 0), a),
                 create_polyline(b, Point(0, 0)),
                 create_polyline(b, Point(0, 0)),
                 create_polyline(b, Point(0, 0))]

    # test polyline joins
    assert len(a.lines) == 3
    assert len(b.lines) == 4

    # construct cluster
    cluster = PolylineCluster()
    cluster.polylines = polylines.copy()
    cluster.bundles = [a, b]

    line = polylines[0].lines[1]
    new_cluster = cluster.split_cluster(line)
    # check split
    assert cluster.polylines == polylines[:3]
    assert len(cluster.polylines[0].lines) == 1
    assert cluster.bundles == [a]
    assert len(new_cluster.polylines) == 3#polylines[-3:]
    assert new_cluster.bundles == [b]

    # 4. case
    # \  /
    #  x-
    # /  \
    #########
    # bundles
    a = Point(0, 0)
    b = Point(0, 0)

    polylines = [create_polyline(a, b, 2),
                 create_polyline(Point(0, 0), a),
                 create_polyline(Point(0, 0), a),
                 create_polyline(b, Point(0, 0)),
                 create_polyline(b, Point(0, 0))]

    # test polyline joins
    assert len(a.lines) == 3
    assert len(b.lines) == 3

    # construct cluster
    cluster = PolylineCluster()
    cluster.polylines = polylines.copy()
    cluster.bundles = [a, b]

    line = polylines[0].lines[0]
    new_cluster = cluster.split_cluster(line)
    # check split
    assert len(cluster.polylines ) == 1
    assert len(cluster.polylines[0].lines) == 4
    assert len(cluster.bundles) == 0
    assert len(new_cluster.polylines) == 3
    assert len(new_cluster.polylines[0].lines) == 1
    assert new_cluster.polylines[1:] == polylines[-2:]
    assert new_cluster.bundles == [b]

    # 5. case
    # \  /
    # -x-
    # /  \
    #########
    # bundles
    a = Point(0, 0)
    b = Point(0, 0)

    polylines = [create_polyline(a, b, 2),
                 create_polyline(Point(0, 0), a),
                 create_polyline(Point(0, 0), a),
                 create_polyline(Point(0, 0), a),
                 create_polyline(b, Point(0, 0)),
                 create_polyline(b, Point(0, 0))]

    # test polyline joins
    assert len(a.lines) == 4
    assert len(b.lines) == 3

    # construct cluster
    cluster = PolylineCluster()
    cluster.polylines = polylines.copy()
    cluster.bundles = [a, b]

    line = polylines[0].lines[0]
    new_cluster = cluster.split_cluster(line)
    # check split
    assert cluster.polylines == polylines[1:4]
    assert cluster.bundles == [a]
    assert len(new_cluster.polylines) == 3
    assert len(new_cluster.polylines[0].lines) == 1
    assert new_cluster.polylines[1:] == polylines[-2:]
    assert new_cluster.bundles == [b]

    def test_try_split_by_bundle(self):
        p = [Point(0, 0), Point(0, 0), Point(0, 0)]
        l = [Line(p[0], p[1]), Line(p[1], p[2])]

        a = Polyline()
        a.lines = l.copy()
        a.points = p.copy()

        c = PolylineCluster()
        c.polylines = [a]

        l2 = Line(Point(0, 0), Point(0, 0))

        assert c.try_split_by_bundle(p[1], l2)
        # check splitted polyline
        assert c.polylines[0].lines == l[:1]
        assert c.polylines[0].points == p[:2]
        assert c.polylines[1].lines == l[1:]
        assert c.polylines[1].points == p[1:]
        assert c.polylines[2].lines == [l2]
        assert c.polylines[2].points == [l2.p1, l2.p2]
        assert c.bundles == [p[1]]
